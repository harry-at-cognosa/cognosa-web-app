"""LLM access for chat: a message list in, text out, streamed asynchronously.

Separate from the Queries runner's provider classes (`tasks_lib/llm_lib`),
which build a single-string prompt and are synchronous. The per-provider
settings below mirror theirs so that an LLM row behaves the same in both.
"""
import asyncio
from typing import AsyncGenerator
from pydantic import SecretStr
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from common.enums.gllms_types import GLLMsTypes
from common.parsed_url import ParsedUrl
from common.sql_models import GroupLLMs

LLM_MAX_TOKENS = 10000   # as the Queries runner
LLM_TIMEOUT_SEC = 120

OPENAI_COMPATIBLE_TYPES = (
    GLLMsTypes.OLLAMA_LOCAL, GLLMsTypes.OLLAMA_REMOTE, GLLMsTypes.CHATGPT, GLLMsTypes.QWEN, GLLMsTypes.MISTRAL,
)


def content_text(content) -> str:
    """Text of a message or chunk. Providers return either a string or a list
    of content blocks (Claude and Gemini do the latter for some responses)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get('type', 'text') == 'text':
                parts.append(str(block.get('text', '')))
        return ''.join(parts)
    return ''


class DummyChatModel:
    """Stands in for an LLM row of type 'dummy': no external call."""
    def __init__(self) -> None:
        self.is_dummy = True

    @staticmethod
    def _answer(messages: list[BaseMessage]) -> str:
        last = content_text(messages[-1].content) if messages else ''
        return f"Dummy answer to: {last}\n\nThis is a simulated answer for testing only."

    async def astream(self, messages: list[BaseMessage]):
        text = self._answer(messages)
        for i in range(0, len(text), 12):
            await asyncio.sleep(0.05)
            yield text[i:i + 12]

    async def ainvoke(self, messages: list[BaseMessage]) -> str:
        return self._answer(messages)


def build_chat_model(gllms: GroupLLMs, max_tokens: int = LLM_MAX_TOKENS) -> BaseChatModel | DummyChatModel:
    llm_type = gllms.gllms_type
    api_key = SecretStr(gllms.gllms_api_key or '')
    if llm_type == GLLMsTypes.DUMMY:
        return DummyChatModel()
    if llm_type in OPENAI_COMPATIBLE_TYPES:
        from langchain_openai import ChatOpenAI
        # 'ollama_local' and similar names resolve to a URL; OpenAI itself uses the SDK default
        base_url = None if llm_type == GLLMsTypes.CHATGPT else ParsedUrl.from_url(gllms.gllms_api_base).full_url
        return ChatOpenAI(
            model=gllms.gllms_model,
            api_key=api_key if gllms.gllms_api_key else SecretStr('none'),  # Ollama needs no key but the SDK wants one
            base_url=base_url,
            temperature=0.0,
            max_completion_tokens=max_tokens,
            timeout=LLM_TIMEOUT_SEC,
            streaming=True,
        )
    if llm_type == GLLMsTypes.CLAUDE:
        from langchain_anthropic import ChatAnthropic
        # No `temperature`: Claude Opus 5 / Sonnet 5 / Opus 4.7+ reject sampling parameters.
        return ChatAnthropic(
            model_name=gllms.gllms_model,
            api_key=api_key,
            timeout=LLM_TIMEOUT_SEC,
            stop=None,
            max_tokens_to_sample=max_tokens,
            streaming=True,
        )
    if llm_type == GLLMsTypes.GEMINI:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=gllms.gllms_model,
            google_api_key=api_key,
            temperature=0.0,
            max_output_tokens=max_tokens,
            timeout=LLM_TIMEOUT_SEC,
        )
    raise NotImplementedError(f"LLM type not supported in chat: {llm_type}")


async def astream_text(model, messages: list[BaseMessage]) -> AsyncGenerator[str, None]:
    """Yield the answer as text pieces as the provider produces them."""
    async for chunk in model.astream(messages):
        text = chunk if isinstance(chunk, str) else content_text(chunk.content)
        if text:
            yield text


async def complete_text(model, messages: list[BaseMessage]) -> str:
    """One non-streamed completion (used for the question rewrite)."""
    result = await model.ainvoke(messages)
    return result if isinstance(result, str) else content_text(result.content)
