from tasks_lib.llm_lib.llm_ops import LLMOps
from time import time

llm_ops = LLMOps('', '', '', '', 'ollama-local', 'http://localhost:11434/v1', 'gemma3', 'api_key')
t1 = time()
print(llm_ops.check_working())
print(time()-t1)