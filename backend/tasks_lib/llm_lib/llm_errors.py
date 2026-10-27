"""Map provider SDK exceptions to a short, user-facing status text.

Every provider adapter (Claude, OpenAI, Gemini) raises its own SDK exception
from inside `stream_to_llm()`. The Anthropic and OpenAI SDKs expose the HTTP
status as `status_code` and the server message as `message`; google-genai uses
`code` and `message`. Connection failures surface as `APIConnectionError` /
`APITimeoutError` (both SDKs) or as httpx / requests transport errors.

The worker stores the full traceback separately (`doc_tasks.exc_text`), so
this only has to produce the one line a user sees in the query page.
"""
import httpx
import requests

# Appended to the status line after the provider's own message.
_MAX_PROVIDER_MSG = 300

_CONNECTION_ERRORS = (httpx.TransportError, requests.RequestException)
_CONNECTION_CLASS_NAMES = ('APIConnectionError', 'APITimeoutError')


def _status_code(exc: BaseException) -> int | None:
    for attr in ('status_code', 'code'):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    return None


def _provider_message(exc: BaseException) -> str:
    """The server's own message when the SDK carries one, else str(exc).

    The Anthropic/OpenAI `message` already includes the status code and the
    raw JSON body; the body's inner `message` is the readable part.
    """
    body = getattr(exc, 'body', None)
    if isinstance(body, dict):
        inner = body.get('error', body)
        if isinstance(inner, dict) and isinstance(inner.get('message'), str):
            return inner['message']
    message = getattr(exc, 'message', None)
    if isinstance(message, str) and message:
        return message
    return str(exc)


def _is_connection_error(exc: BaseException) -> bool:
    if isinstance(exc, _CONNECTION_ERRORS):
        return True
    return any(cls.__name__ in _CONNECTION_CLASS_NAMES for cls in type(exc).__mro__)


def classify_llm_exception(exc: BaseException) -> str:
    """Return a one-line status for `doc_tasks.status_text` (caller truncates).

    Falls back to the historical "Undefined LLM error" when nothing more
    specific can be said, so existing UI behaviour is unchanged for unknown
    failures.
    """
    if _is_connection_error(exc):
        return "LLM provider unreachable (connection error or timeout)"

    code = _status_code(exc)
    if code is None:
        return "Undefined LLM error"

    msg = _provider_message(exc)
    lowered = msg.lower()
    if code == 400 and ('credit balance' in lowered or 'billing' in lowered or 'quota' in lowered):
        label = "LLM provider billing error"
    elif code == 400:
        label = "LLM request rejected by provider"
    elif code == 401:
        label = "LLM API key rejected"
    elif code == 403:
        label = "LLM API key lacks permission"
    elif code == 404:
        label = "LLM model not found"
    elif code == 429:
        label = "LLM rate limited or quota exhausted"
    elif code >= 500:
        label = "LLM provider unavailable"
    else:
        label = "LLM provider error"

    return f"{label} (HTTP {code}): {msg[:_MAX_PROVIDER_MSG]}"
