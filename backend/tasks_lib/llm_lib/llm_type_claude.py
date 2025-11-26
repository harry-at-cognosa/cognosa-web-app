from typing import Generator
from urllib.parse import quote
from pydantic import SecretStr
import httpx
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from pydantic import SecretStr
from common import log
from tasks_lib.cmd_line_opts import LLM_PROXY


class LLMTypeClaude:
    BASE_URL = 'https://api.anthropic.com/v1'    
    def __init__(
            self, 
            query_text: str, 
            template: str, 
            llm_type: str,
            llm_model: str, 
            llm_api_key: str
        ) -> None:
        self.query_text = query_text
        self.template = template
        self.llm_type = llm_type
        self.llm_model = llm_model
        self.llm_api_key = SecretStr(llm_api_key)
        self.temperature = 0.0
        self.llm_max_tokens = 10000
        self.sent_to_llm: str = ''
        self.answer: str = ''

    def check_working(self) -> bool:
        """
        Check if LLM model is available
        """
        try:
            full_url = self.BASE_URL + quote(f'/models/{self.llm_model}')
            client = httpx.Client(
                proxy=LLM_PROXY,
                timeout=10.0,
                headers={
                    "x-api-key": self.llm_api_key.get_secret_value(),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            if client.get(full_url).status_code == 200:
                return True
        except Exception:
            pass
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
        
        llm = ChatAnthropic(
            model_name=self.llm_model, 
            api_key=self.llm_api_key, 
            timeout=60, 
            stop=None, 
            anthropic_proxy=LLM_PROXY, 
            temperature=self.temperature,
            max_tokens_to_sample=self.llm_max_tokens,
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
