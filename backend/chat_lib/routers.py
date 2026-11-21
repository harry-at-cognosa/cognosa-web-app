from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from common.sql_db_async import AsyncSession, async_get_session
from common.sql_models import User
from chat_lib.auth import chat_user
from chat_lib.schemas import (
    ChatOptions, ChatOptionsCollection, ChatOptionsLLM,
    ConversationCreate, ConversationRename, ConversationRead, ConversationDetail, DeleteResult, MessageCreate,
)
from chat_lib.tables import ChatTable, ChatError
from chat_lib.turn import prepare_turn, stream_turn

router__chat = APIRouter()


@router__chat.get("/options", response_model=ChatOptions)
async def get_options(user: User = Depends(chat_user), session: AsyncSession = Depends(async_get_session)):
    """Collections and LLMs the caller's group may chat with."""
    table = ChatTable(session, user)
    collections = await table.list_collections()
    llms = await table.list_llms()
    return ChatOptions(
        collections=[ChatOptionsCollection(
            gvdbs_id=c.gvdbs_id, gvdbs_name=c.gvdbs_name, gvdbs_status=c.gvdbs_status,
            gvdbs_retr_filters=c.gvdbs_retr_filters) for c in collections],
        llms=[ChatOptionsLLM(gllms_id=m.gllms_id, gllms_name=m.gllms_name, gllms_status=m.gllms_status) for m in llms],
    )


@router__chat.get("/conversations", response_model=list[ConversationRead])
async def list_conversations(user: User = Depends(chat_user), session: AsyncSession = Depends(async_get_session)):
    return await ChatTable(session, user).list_conversations()


@router__chat.post("/conversations", response_model=ConversationRead, status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    user: User = Depends(chat_user),
    session: AsyncSession = Depends(async_get_session),
):
    try:
        return await ChatTable(session, user).create_conversation(payload.gvdbs_id, payload.gllms_id, payload.filters)
    except ChatError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router__chat.get("/conversations/{conv_id:int}", response_model=ConversationDetail)
async def get_conversation(
    conv_id: int, user: User = Depends(chat_user), session: AsyncSession = Depends(async_get_session)):
    result = await ChatTable(session, user).get_conversation(conv_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router__chat.patch("/conversations/{conv_id:int}", response_model=ConversationRead)
async def rename_conversation(
    conv_id: int,
    payload: ConversationRename,
    user: User = Depends(chat_user),
    session: AsyncSession = Depends(async_get_session),
):
    """Rename only: the collection and filters of a conversation are fixed."""
    result = await ChatTable(session, user).rename_conversation(conv_id, payload.title)
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router__chat.delete("/conversations/{conv_id:int}", response_model=DeleteResult)
async def delete_conversation(
    conv_id: int, user: User = Depends(chat_user), session: AsyncSession = Depends(async_get_session)):
    success = await ChatTable(session, user).delete_conversation(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return DeleteResult(conv_id=conv_id, success=True)


@router__chat.post("/conversations/{conv_id:int}/messages")
async def send_message(
    conv_id: int,
    payload: MessageCreate,
    user: User = Depends(chat_user),
    session: AsyncSession = Depends(async_get_session),
):
    """Send a message; the answer comes back as a stream of server-sent events.
    Closing the stream stops the answer (what was written so far is kept)."""
    try:
        ctx = await prepare_turn(session, user, conv_id, payload.content, payload.gllms_id)
    except ChatError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return StreamingResponse(
        stream_turn(ctx),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # the latter: no buffering in nginx
    )
