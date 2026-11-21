"""Question rewrite: turn a follow-up into a standalone question before searching.

"What about the dimmable one?" cannot be searched as typed. The earlier turns
are given to an LLM, which restates the follow-up so that it stands alone.
The result is what gets embedded, and is stored as `retrieval_query`.
"""
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage
from common import log
from chat_lib.llm_providers import complete_text

REWRITE_TIMEOUT_SEC = 45
# How much of each earlier answer the rewrite sees; enough to resolve references.
REWRITE_ANSWER_CHARS = 1500
REWRITE_MAX_CHARS = 2000

REWRITE_SYSTEM_PROMPT = (
    "You rewrite a follow-up message from a conversation as a single standalone question "
    "that can be understood without the conversation, for use as a document search query.\n"
    "- Replace pronouns and vague references with the specific things they refer to.\n"
    "- Keep every name, identifier, number and unit exactly as written.\n"
    "- Keep the language of the follow-up message.\n"
    "- If the follow-up already stands alone, return it unchanged.\n"
    "- Do not answer the question. Output only the rewritten question, with no preamble or quotes."
)


def _format_history(history: list[tuple[str, str]]) -> str:
    lines = []
    for question, answer in history:
        answer = answer if len(answer) <= REWRITE_ANSWER_CHARS else answer[:REWRITE_ANSWER_CHARS] + " ..."
        lines.append(f"User: {question}\nAssistant: {answer}")
    return "\n\n".join(lines)


async def rewrite_question(model, history: list[tuple[str, str]], user_message: str) -> str:
    """The standalone form of `user_message`. Falls back to the message as
    typed if there is no history or the rewrite call fails: a weaker search is
    better than a failed turn."""
    if not history:
        return user_message
    messages = [
        SystemMessage(content=REWRITE_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Conversation so far:\n\n{_format_history(history)}\n\n"
            f"Follow-up message:\n{user_message}\n\n"
            "Standalone question:"
        )),
    ]
    try:
        text = await asyncio.wait_for(complete_text(model, messages), timeout=REWRITE_TIMEOUT_SEC)
        text = text.strip().strip('"').strip()
        if text and len(text) <= REWRITE_MAX_CHARS:
            return text
        log.error(f"Chat rewrite returned an unusable result ({len(text)} chars); using the message as typed")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        log.error(f"Chat rewrite failed ({type(exc).__name__}: {exc}); using the message as typed")
    return user_message
