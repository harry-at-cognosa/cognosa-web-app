from time import sleep
from typing import Generator
from common.helpers import chunks

fake_answer = """
# This is simulated answer from LLM.
## For testing only. 

# Petunt unda rudem

## Ignem corpore coniecit sed

Lorem markdownum stellatus tamen spretarumque inpius palato bisulcam operi *non
Thyneius postquam*. Ore alta fratrum aerane Iunone accepisse misit auctorem quo
formis vicinia, pastoribus citharae equumque inde `windows_optic_transfer`
quamquam. Cibique suis arbusta.
"""

class LLMTypeDummy:
    def __init__(
            self, 
            query_text: str, 
            ) -> None:
        self.query_text = query_text
        self.sent_to_llm: str = ''
        self.answer: str = ''

    def check_working(self) -> bool:
        return True
    
    def stream_to_llm(self, full_context: str) -> Generator[str, None, None]:
        self.sent_to_llm = full_context \
            .replace('{question}', self.query_text) \
            .replace('{context}', full_context)
        dummy_answer = f"Dummy answer to query:\n{self.query_text}\n{fake_answer}"
        self.answer = ''
        for chunk in chunks(list(dummy_answer), 50):
            chunk_str = ''.join(chunk)
            self.answer += chunk_str
            yield chunk_str
            sleep(1)
        return