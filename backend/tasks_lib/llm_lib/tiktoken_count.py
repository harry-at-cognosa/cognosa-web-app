import tiktoken


class TikTokenCount:
    def __init__(self, llm_model: str) -> None:
        self.llm_model = llm_model
        self.encoding = self.get_tiktoken_encoding_from_llm()
        
    def get_tiktoken_encoding_from_llm(self):
        """
        Try to get token encoding from llm.
        If failed, use the encoding from gpt-4o.
        """
        try:
            return tiktoken.encoding_for_model(self.llm_model)
        except KeyError:
            return tiktoken.get_encoding("o200k_base")

    def count(self, text: str) -> int:
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return 0
