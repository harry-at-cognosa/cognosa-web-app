"""One chat turn: user message in, streamed answer out.

The turn runs as its own task and reports through a queue; the HTTP response
only relays the queue. That way a browser that goes away (or presses Stop,
which closes the stream) cancels the turn cleanly, and the partial answer is
still saved.

Server-sent events emitted:
    status  {"text": "..."}            progress line
    token   {"t": "..."}               a piece of the answer
    done    {"msg_id", "status", "retrieval_query", "tokens_in", "tokens_out", "seconds", "title"}
    error   {"text": "...", "msg_id"}  the turn failed; the text is also stored as the answer
"""
import asyncio
import json
from dataclasses import dataclass, field
from time import time
from traceback import format_exc
from typing import AsyncGenerator
from sqlalchemy import select, func
from common import log
from common.features.chat_cfg import ChatCfg, parse_chat_history_turns
from common.sql_db_async import AsyncSession, SqlAsyncSession
from common.sql_models import User, ApiGroups, GroupVDBs, GroupLLMs, ChatConversations, ChatMessages
from common.sql_models.chat_messages import ChatMessageRole, ChatMessageStatus
from common.sql_models.doc_tasks import SHORT_NAME_DEFAULT_LEN
from cwa_lib.sql_tables.api_settings import ApiSettingsTable
from tasks_lib.llm_lib.llm_errors import classify_llm_exception
from tasks_lib.llm_lib.tiktoken_count import TikTokenCount
from chat_lib.llm_providers import build_chat_model, astream_text
from chat_lib.prompt import build_messages, messages_text
from chat_lib.retrieval import retrieve
from chat_lib.rewrite import rewrite_question
from chat_lib.tables import ChatTable, ChatError

MESSAGE_MAX_CHARS = 20_000
# The rewrite is a short task; no need for the answer's token allowance.
REWRITE_MAX_TOKENS = 2000

# Conversations with an answer being written. One process, so a set is enough.
_in_flight: set[int] = set()
# Keep references to running turn tasks so they are not garbage-collected.
_tasks: set[asyncio.Task] = set()


def _db_text(s: str) -> str:
    # PostgreSQL rejects NUL bytes in text columns
    return s.replace('\x00', '')


@dataclass
class TurnContext:
    """Everything a turn needs, read once while the request's session is open."""
    conv_id: int
    user_id: int
    group_id: int
    user_message: str
    collection: GroupVDBs
    filters_json: str | None
    llm: GroupLLMs
    rewrite_llm: GroupLLMs
    history: list[tuple[str, str]]
    set_title: str | None
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)


def _history_turns(messages: list[ChatMessages], limit: int) -> list[tuple[str, str]]:
    """Earlier turns as (question, answer) pairs, oldest first, at most `limit`.
    A turn counts when its answer finished or was stopped with some text;
    failed turns are left out."""
    turns: list[tuple[str, str]] = []
    for i in range(len(messages) - 1):
        q, a = messages[i], messages[i + 1]
        if q.role != ChatMessageRole.USER or a.role != ChatMessageRole.ASSISTANT:
            continue
        if a.status not in (ChatMessageStatus.COMPLETE, ChatMessageStatus.STOPPED) or not a.content.strip():
            continue
        turns.append((q.content, a.content))
    return turns[-limit:] if limit > 0 else []


async def _next_seqn(session: AsyncSession, conv_id: int) -> int:
    current = (await session.execute(
        select(func.max(ChatMessages.seqn)).where(ChatMessages.conv_id == conv_id))).scalar()
    return (current or 0) + 1


async def prepare_turn(session: AsyncSession, user: User, conv_id: int, content: str, gllms_id: int) -> TurnContext:
    """Validate the request, store the user's message and collect what the
    turn needs. Raises ChatError for anything the caller got wrong."""
    content = _db_text(content or '').strip()
    if not content:
        raise ChatError("Enter a message")
    if len(content) > MESSAGE_MAX_CHARS:
        raise ChatError(f"Message is too long (limit {MESSAGE_MAX_CHARS} characters)")

    table = ChatTable(session, user)
    conv = await table.get_conversation_row(conv_id)
    if not conv:
        raise ChatError("Conversation not found", status_code=404)
    if conv_id in _in_flight:
        raise ChatError("An answer is still being written in this conversation", status_code=409)

    collection = await table.get_collection(conv.gvdbs_id)
    if not collection:
        raise ChatError("The document collection of this conversation is no longer available")
    if collection.gvdbs_status == 'danger':
        raise ChatError("Document collection is not ready")
    llm = await table.get_llm(gllms_id)
    if not llm:
        raise ChatError("LLM not found")
    if llm.gllms_status == 'danger':
        raise ChatError("LLM is not ready")

    # Rewrite LLM: the group's designated one when set and usable, else this turn's LLM.
    rewrite_llm = llm
    group = await session.get(ApiGroups, user.group_id)
    if group and group.chat_rewrite_gllms_id:
        candidate = await table.get_llm(group.chat_rewrite_gllms_id)
        if candidate and candidate.gllms_status != 'danger':
            rewrite_llm = candidate

    history_limit = parse_chat_history_turns(await ApiSettingsTable(session).select_one('chat_history_turns'))
    earlier = list((await session.execute(
        select(ChatMessages).where(ChatMessages.conv_id == conv_id).order_by(ChatMessages.seqn))).scalars().all())
    history = _history_turns(earlier, history_limit)

    set_title = None
    if not conv.title.strip():
        set_title = content[:SHORT_NAME_DEFAULT_LEN].rstrip()

    ctx = TurnContext(
        conv_id=conv_id, user_id=user.user_id, group_id=user.group_id, user_message=content,
        collection=collection, filters_json=conv.filters_json, llm=llm, rewrite_llm=rewrite_llm,
        history=history, set_title=set_title,
    )
    # These rows are read again after the request's session is gone.
    for row in (collection, llm, rewrite_llm):
        session.expunge(row) if row in session else None

    _in_flight.add(conv_id)
    try:
        session.add(ChatMessages(
            conv_id=conv_id, seqn=await _next_seqn(session, conv_id),
            role=ChatMessageRole.USER, content=content, status=ChatMessageStatus.COMPLETE,
        ))
        values = {'updated_at': func.now(), 'gllms_id': llm.gllms_id}
        if set_title:
            values['title'] = set_title
        await session.execute(
            ChatConversations.__table__.update().where(ChatConversations.conv_id == conv_id).values(**values))
        await session.commit()
    except Exception:
        _in_flight.discard(conv_id)
        raise
    return ctx


async def _save_answer(ctx: TurnContext, content: str, status: str, retrieval_query: str | None,
                       tokens_in: int | None, tokens_out: int | None, seconds: float | None) -> int:
    """The single write of an assistant message."""
    async with SqlAsyncSession() as session:
        row = ChatMessages(
            conv_id=ctx.conv_id, seqn=await _next_seqn(session, ctx.conv_id),
            role=ChatMessageRole.ASSISTANT, content=_db_text(content), status=status,
            gllms_id=ctx.llm.gllms_id, retrieval_query=_db_text(retrieval_query) if retrieval_query else None,
            tokens_in=tokens_in, tokens_out=tokens_out, seconds=seconds,
        )
        session.add(row)
        await session.execute(
            ChatConversations.__table__.update()
            .where(ChatConversations.conv_id == ctx.conv_id).values(updated_at=func.now()))
        await session.commit()
        return row.msg_id


async def _run_turn(ctx: TurnContext) -> None:
    put = ctx.queue.put_nowait
    started = time()
    answer = ''
    retrieval_query: str | None = None
    tokens_in: int | None = None
    counter = TikTokenCount(ctx.llm.gllms_model)

    def elapsed() -> float:
        return round(time() - started, 3)

    try:
        # 1. Standalone question (only when there is something to refer back to)
        if ctx.history:
            put(('status', {'text': 'Understanding the question...'}))
            rewrite_model = build_chat_model(ctx.rewrite_llm, max_tokens=REWRITE_MAX_TOKENS)
            retrieval_query = await rewrite_question(rewrite_model, ctx.history, ctx.user_message)
            log.info(f"Chat conv {ctx.conv_id}: rewrite by '{ctx.rewrite_llm.gllms_name}' -> {retrieval_query!r}")
        else:
            retrieval_query = ctx.user_message

        # 2. Search
        put(('status', {'text': 'Searching the documents...'}))
        chat_cfg = ChatCfg.from_str(ctx.collection.gvdbs_chat_cfg)
        retr_params = chat_cfg.get_retr_params(ctx.collection.gvdbs_retr_params)
        docs = await retrieve(ctx.collection, retrieval_query, retr_params, ctx.filters_json)
        log.info(f"Chat conv {ctx.conv_id}: {len(docs)} chunks, params {retr_params}, "
                 f"filters {'yes' if ctx.filters_json else 'no'}")

        # 3. Answer. The chunks live only in `messages` and are dropped after this call.
        messages = build_messages(chat_cfg.get_system_prompt(), docs, ctx.history, ctx.user_message)
        tokens_in = counter.count(messages_text(messages))
        put(('status', {'text': 'Answering...'}))
        model = build_chat_model(ctx.llm)
        async for text in astream_text(model, messages):
            answer += text
            put(('token', {'t': text}))

        msg_id = await _save_answer(
            ctx, answer, ChatMessageStatus.COMPLETE, retrieval_query, tokens_in, counter.count(answer), elapsed())
        put(('done', {
            'msg_id': msg_id, 'status': ChatMessageStatus.COMPLETE, 'retrieval_query': retrieval_query,
            'tokens_in': tokens_in, 'tokens_out': counter.count(answer), 'seconds': elapsed(),
            'title': ctx.set_title,
        }))
    except asyncio.CancelledError:
        # The browser closed the stream (Stop, or it went away). Keep what was written.
        log.info(f"Chat conv {ctx.conv_id}: stopped after {len(answer)} characters")
        try:
            await _save_answer(
                ctx, answer, ChatMessageStatus.STOPPED, retrieval_query, tokens_in,
                counter.count(answer) if answer else 0, elapsed())
        except Exception:
            log.error(f"Chat conv {ctx.conv_id}: cannot save stopped answer:\n{format_exc()}")
    except Exception as exc:
        log.error(f"Chat conv {ctx.conv_id}: turn failed:\n{format_exc()}")
        text = classify_llm_exception(exc)
        if text == "Undefined LLM error":
            text = f"The answer could not be produced ({type(exc).__name__})."
        # Whatever was streamed before the failure is kept above the error line.
        content = (answer + "\n\n" if answer else "") + text
        msg_id = None
        try:
            msg_id = await _save_answer(
                ctx, content, ChatMessageStatus.ERROR, retrieval_query, tokens_in,
                counter.count(answer) if answer else 0, elapsed())
        except Exception:
            log.error(f"Chat conv {ctx.conv_id}: cannot save error message:\n{format_exc()}")
        put(('error', {'text': text, 'msg_id': msg_id}))
    finally:
        _in_flight.discard(ctx.conv_id)
        put(None)  # end of stream


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_turn(ctx: TurnContext) -> AsyncGenerator[str, None]:
    """Run the turn and relay its events as server-sent events."""
    task = asyncio.create_task(_run_turn(ctx), name=f'chat_turn_{ctx.conv_id}')
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    try:
        while True:
            item = await ctx.queue.get()
            if item is None:
                break
            yield _sse(*item)
    finally:
        # Reached with the task still running only when the client is gone.
        if not task.done():
            task.cancel()
