import json
from time import sleep
from typing import Generator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr
from tasks_lib.cmd_line_opts import IS_DUMMY_LLM
from .dummy import DummyLLM
from common.helpers import chunks


class LLMOps:
    def __init__(self, 
                 query_text: str, 
                 optional_text: str,
                 template: str, 
                 context_json_str: str | None, 
                 llm_api_base: str, 
                 llm_model_name: str, 
                 llm_api_key: str
                 ) -> None:
        self.query_text = query_text
        if optional_text and optional_text.strip():
            self.query_text += f'\n   \n{optional_text.strip()}\n   '
        self.optional_text = optional_text
        self.template = template
        self.context_json_str = context_json_str if context_json_str else '[]'
        self.llm_api_base = llm_api_base
        self.llm_model_name = llm_model_name
        self.llm_api_key = SecretStr(llm_api_key)
        self.top_k = 4
        self.temperature = 0.0
        self.llm_max_tokens = 500
        self.context_json: str = ''
        self.answer: str = ''


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
    
    def stream_to_llm(self) -> Generator[str, None, None]:
        # Initialize LLM
        if IS_DUMMY_LLM:
            dummy_answer = f"Dummy answer to query:\n{self.query_text}\n{DummyLLM.fake_answer}"
            self.answer = ""
            for chunk in chunks(list(dummy_answer), 50):
                chunk_str = ''.join(chunk)
                self.answer += chunk_str
                yield chunk_str
                sleep(1)
            return
        full_context = self.prepare_context()
        llm = ChatOpenAI(
            model=self.llm_model_name,
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
            | llm
            | StrOutputParser()
        )
        
        # Stream the response
        for chunk in rag_chain.stream(self.query_text):
            self.answer += chunk
            yield chunk
