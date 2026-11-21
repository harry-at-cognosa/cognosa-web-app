"""Assembly of what is sent to the LLM for a chat turn."""
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


def format_context(docs: list[dict]) -> str:
    """Retrieved chunks as one text block, in the layout the Queries runner uses."""
    parts = []
    for i, doc in enumerate(docs):
        part = f"Document {i + 1}:\n{doc['page_content']}"
        if doc.get('metadata'):
            part += f"\nMetadata: {doc['metadata']}"
        parts.append(part)
    return "\n\n".join(parts)


def build_messages(
        system_prompt: str, docs: list[dict], history: list[tuple[str, str]], user_message: str) -> list[BaseMessage]:
    """System prompt carrying this turn's chunks, the earlier turns as plain
    question/answer text, then the new message.

    Only the current turn's chunks are sent; earlier turns contribute their
    text, not the chunks that were retrieved for them.
    """
    context = format_context(docs) if docs else "(No documents were found for this question.)"
    # str.replace, not str.format: prompts and chunks may contain braces
    messages: list[BaseMessage] = [SystemMessage(content=system_prompt.replace('{context}', context))]
    for question, answer in history:
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=answer))
    messages.append(HumanMessage(content=user_message))
    return messages


def messages_text(messages: list[BaseMessage]) -> str:
    """Everything sent, as one string, for token counting."""
    return "\n".join(str(m.content) for m in messages)
