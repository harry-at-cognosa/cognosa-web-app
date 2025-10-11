import json
from time import sleep
from typing import Generator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
import requests
from pydantic import SecretStr
from tasks_lib.cmd_line_opts import IS_DUMMY_LLM
from .dummy import DummyLLM
from common import log
from common.helpers import chunks
from common.parsed_url import ParsedUrl
from common.enums.gllms_types import GLLMsTypes


class LLMOps:
    def __init__(self, 
                 query_text: str, 
                 optional_text: str,
                 template: str, 
                 context_json_str: str | None, 
                 llm_type: str,
                 llm_api_base: str, 
                 llm_model: str, 
                 llm_api_key: str
                 ) -> None:
        self.query_text = query_text
        if optional_text and optional_text.strip():
            self.query_text += f'\n   \n{optional_text.strip()}\n   '
        self.optional_text = optional_text
        self.template = template
        self.context_json_str = context_json_str if context_json_str else '[]'
        self.llm_type = llm_type
        self.llm_api_base = llm_api_base
        self.llm_model = llm_model
        self.llm_api_key = SecretStr(llm_api_key)
        self.top_k = 4
        self.temperature = 0.0
        self.llm_max_tokens = 500
        self.context_json: str = ''
        self.sent_to_llm: str = ''
        self.answer: str = ''

    def check_working(self) -> bool:
        """
        Check if LLM is working
        """
        if self.llm_type == GLLMsTypes.DUMMY:
            return True
        try:
            parsed_url = ParsedUrl.from_url(self.llm_api_base)  # to convert localhost -> 127.0.0.1
            parsed_url.path = 'v1/models'
            return requests.get(parsed_url.full_url, timeout=5).status_code == 200
        except Exception:
            return False

    def prepare_context(self) -> str:
        # Prepare context for LLM
        context_json = json.loads(self.context_json_str)
        context_parts = []
        for i, doc in enumerate(context_json):
            context_part = f"Document {i+1}:\n{doc['page_content']}"
            if doc.get('metadata'):
                context_part += f"\nMetadata: {doc['metadata']}"
            context_parts.append(context_part)
        
        # Combine all context
        return "\n\n".join(context_parts)
    
    def _stream_dummy_answer(self) -> Generator[str, None, None]:
        dummy_answer = f"Dummy answer to query:\n{self.query_text}\n{DummyLLM.fake_answer}"
        self.answer = ""
        for chunk in chunks(list(dummy_answer), 50):
            chunk_str = ''.join(chunk)
            self.answer += chunk_str
            yield chunk_str
            sleep(1)
        return
    
    def stream_to_llm(self) -> Generator[str, None, None]:
        # Initialize LLM
        if IS_DUMMY_LLM or (self.llm_type == GLLMsTypes.DUMMY):
            yield from self._stream_dummy_answer()
            return
        
        def capture_prompt(prompt_value):
            if isinstance(prompt_value, StringPromptValue):
                self.sent_to_llm = str(prompt_value.text)
            else:
                log.error(f"Prompt value is not StringPromptValue, but {type(prompt_value)}")
            return prompt_value

        full_context = self.prepare_context()
        llm = ChatOpenAI(
            model=self.llm_model,
            api_key=self.llm_api_key,
            base_url=self.llm_api_base,
            temperature=self.temperature,
            max_completion_tokens=self.llm_max_tokens,
            streaming=True
        )
        # Create prompt template        
        prompt = PromptTemplate.from_template(self.template)
        
        # Create RAG chain
        rag_chain = (
            {"context": lambda x: full_context, "question": RunnablePassthrough()}
            | prompt
            | RunnableLambda(capture_prompt) 
            | llm
            | StrOutputParser()
        )
        # Stream the response
        for chunk in rag_chain.stream(self.query_text):
            self.answer += chunk
            yield chunk
