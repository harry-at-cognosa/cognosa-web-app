from typing import Generator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from pydantic import SecretStr
import httpx
from common import log


class LLMTypeGemini:
    BASE_URL = 'https://generativelanguage.googleapis.com/v1'
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
        Check if LLM is working
        """
        try:
            full_url = self.BASE_URL + '/models'
            client = httpx.Client(
                timeout=5.0,
                params={'key': self.llm_api_key.get_secret_value()}
            )
            result = client.get(full_url)
            r = result.json()
            name_list = [x['name'].replace('models/', '') for x in r['models']]
            return self.llm_model in name_list
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

        llm = ChatGoogleGenerativeAI(
            model=self.llm_model,
            google_api_key=self.llm_api_key,
            temperature=self.temperature,
            max_output_tokens=self.llm_max_tokens,
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
