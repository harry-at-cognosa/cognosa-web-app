from typing import Generator
from urllib.parse import quote
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from pydantic import SecretStr
import requests
from common import log
from common.enums.gllms_types import GLLMsTypes
from common.parsed_url import ParsedUrl



class LLMTypeOpenAI:
    def __init__(
            self, 
            query_text: str, 
            template: str, 
            llm_type: str,
            llm_api_base: str, 
            llm_model: str, 
            llm_api_key: str
        ) -> None:
        self.query_text = query_text
        self.template = template
        self.llm_type = llm_type
        self.llm_api_base = llm_api_base
        self.llm_model = llm_model
        self.llm_api_key = SecretStr(llm_api_key)
        self.temperature = 0.0
        self.llm_max_tokens = 10000
        self.sent_to_llm: str = ''
        self.answer: str = ''

    def check_working(self) -> bool:
        """
        Check if LLM is working
        """
        try:
            if self.llm_type == GLLMsTypes.CHATGPT:
                full_url = f"https://api.openai.com/v1/models/{quote(self.llm_model)}"
                headers = {"Authorization": f"Bearer {self.llm_api_key.get_secret_value()}"}
                return requests.get(full_url, timeout=5, headers=headers).status_code == 200
            else:
                parsed_url = ParsedUrl.from_url(self.llm_api_base)
                parsed_url.path = 'v1/models'
                return requests.get(parsed_url.full_url, timeout=5).status_code == 200
        except Exception:
            return False
        
    def stream_to_llm(self, full_context: str) -> Generator[str, None, None]:        
        self.sent_to_llm = ''
        self.answer = ''
        
        # Initialize LLM
        def capture_prompt(prompt_value):
            if isinstance(prompt_value, StringPromptValue):
                self.sent_to_llm = str(prompt_value.text)
            else:
                log.error(f"Prompt value is not StringPromptValue, but {type(prompt_value)}")
            return prompt_value

        llm = ChatOpenAI(
            model=self.llm_model,
            api_key=self.llm_api_key,
            base_url=None if (self.llm_type == GLLMsTypes.CHATGPT) else self.llm_api_base,
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
