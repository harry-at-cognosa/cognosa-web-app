import json
from typing import Generator
from tasks_lib.cmd_line_opts import IS_DUMMY_LLM
from common.enums.gllms_types import GLLMsTypes
from common.parsed_url import ParsedUrl
from .llm_type_dummy import LLMTypeDummy
from .llm_type_openai import LLMTypeOpenAI
from .llm_type_claude import LLMTypeClaude
from .llm_type_gemini import LLMTypeGemini

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
        # convert 'ollama_local', 'ollama_remote' to URL
        llm_api_base = ParsedUrl.from_url(llm_api_base).full_url
        query_text = query_text
        if optional_text and optional_text.strip():
            query_text += f'\n   \n{optional_text.strip()}\n   '
        
        context_json_str = context_json_str if context_json_str else '[]'

        # Dummy LLM
        if IS_DUMMY_LLM or (llm_type == GLLMsTypes.DUMMY):
            self.llm_obj = LLMTypeDummy(query_text=query_text)
        # Ollama / OpenAI LLM
        elif llm_type in (GLLMsTypes.OLLAMA_LOCAL, GLLMsTypes.OLLAMA_REMOTE, GLLMsTypes.CHATGPT):
            self.llm_obj = LLMTypeOpenAI(
                query_text=query_text,
                template=template,
                llm_type=llm_type,
                llm_api_base=llm_api_base,
                llm_model=llm_model,
                llm_api_key=llm_api_key
            )
        # Claude (Anthropic) LLM
        elif llm_type == GLLMsTypes.CLAUDE:
            self.llm_obj = LLMTypeClaude(
                query_text=query_text,
                template=template,
                llm_type=llm_type,
                llm_api_base=llm_api_base,
                llm_model=llm_model,
                llm_api_key=llm_api_key
            )
        elif llm_type == GLLMsTypes.GEMINI:
            self.llm_obj = LLMTypeGemini(
                query_text=query_text,
                template=template,
                llm_type=llm_type,
                llm_model=llm_model,
                llm_api_key=llm_api_key
            )
        else:
            raise NotImplementedError
        
        self.context_json_str = context_json_str if context_json_str else '[]'        

    def check_working(self) -> bool:
        """
        Check if LLM is working
        """
        return self.llm_obj.check_working()

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
        full_context = self.prepare_context()
        yield from self.llm_obj.stream_to_llm(full_context)
        return
