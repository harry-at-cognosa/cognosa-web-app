import json
from sqlalchemy import select, delete, update, func
from common.enums.gvdbs_types import GVDBsTypes
from common.features.gvdbs_retr_filters import (
    FormSchemaGVDBsRF, GVDBsRetrFiltersFunctions, RequestGVDBsRetrFilters,
)
from common.sql_db_async import AsyncSession
from common.sql_models import User, GroupVDBs, GroupLLMs, ChatConversations, ChatMessages
from cwa_lib.sql_tables.group_vdbs_select_values import GroupVDBsSelectValuesTable
from chat_lib.schemas import ConversationRead, ConversationDetail, MessageRead

# Sidebar size. Conversations persist until deleted; this only bounds one listing.
CONVERSATIONS_LIST_LIMIT = 200


class ChatError(Exception):
    """A request the caller got wrong; `detail` is safe to show."""
    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _filters_dict(filters_json: str | None) -> dict | None:
    if not filters_json:
        return None
    try:
        return json.loads(filters_json)
    except Exception:
        return None


def conversation_read(row: ChatConversations) -> ConversationRead:
    return ConversationRead(
        conv_id=row.conv_id, title=row.title, gvdbs_id=row.gvdbs_id, gllms_id=row.gllms_id,
        filters=_filters_dict(row.filters_json), created_at=row.created_at, updated_at=row.updated_at,
    )


class ChatTable:
    """All chat database access. Every read and write is scoped to the caller's
    own user_id and group_id; there is no cross-user or admin access path."""
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.session = session
        self.user = user

    # --- options ---------------------------------------------------------
    async def get_collection(self, gvdbs_id: int) -> GroupVDBs | None:
        """An enabled Qdrant collection of the caller's group, or None."""
        result = await self.session.execute(
            select(GroupVDBs).where(
                GroupVDBs.gvdbs_id == gvdbs_id,
                GroupVDBs.group_id == self.user.group_id,
                GroupVDBs.deleted == 0,
                GroupVDBs.enabled == True,  # noqa: E712
                GroupVDBs.gvdbs_type == GVDBsTypes.QDRANT,
            ))
        return result.scalar_one_or_none()

    async def get_llm(self, gllms_id: int) -> GroupLLMs | None:
        """An enabled LLM of the caller's group, or None."""
        result = await self.session.execute(
            select(GroupLLMs).where(
                GroupLLMs.gllms_id == gllms_id,
                GroupLLMs.group_id == self.user.group_id,
                GroupLLMs.deleted == 0,
                GroupLLMs.enabled == True,  # noqa: E712
            ))
        return result.scalar_one_or_none()

    async def list_collections(self) -> list[GroupVDBs]:
        result = await self.session.execute(
            select(GroupVDBs).where(
                GroupVDBs.group_id == self.user.group_id,
                GroupVDBs.deleted == 0,
                GroupVDBs.enabled == True,  # noqa: E712
                GroupVDBs.gvdbs_type == GVDBsTypes.QDRANT,
            ).order_by(GroupVDBs.gvdbs_seqn, GroupVDBs.gvdbs_id))
        rows = list(result.scalars().all())
        # Fill the values of auto-fill select filters, as the Queries page does.
        for row in rows:
            try:
                schema = FormSchemaGVDBsRF.model_validate_json(row.gvdbs_retr_filters)
                path__values = await GroupVDBsSelectValuesTable(self.session).get_path__values(gvdbs_id=row.gvdbs_id)
                for field in schema.fields:
                    if field.type == 'select' and field.auto_fill:
                        field.values = path__values.get(field.path, [])
                # detach before changing, so the edit is never flushed to the database
                self.session.expunge(row)
                row.gvdbs_retr_filters = schema.model_dump_json()
            except Exception:
                pass  # no filters defined for this collection
        return rows

    async def list_llms(self) -> list[GroupLLMs]:
        result = await self.session.execute(
            select(GroupLLMs).where(
                GroupLLMs.group_id == self.user.group_id,
                GroupLLMs.deleted == 0,
                GroupLLMs.enabled == True,  # noqa: E712
            ).order_by(GroupLLMs.gllms_seqn, GroupLLMs.gllms_id))
        return list(result.scalars().all())

    # --- conversations ---------------------------------------------------
    def _own(self):
        return (ChatConversations.user_id == self.user.user_id) & (ChatConversations.group_id == self.user.group_id)

    async def get_conversation_row(self, conv_id: int) -> ChatConversations | None:
        result = await self.session.execute(
            select(ChatConversations).where(ChatConversations.conv_id == conv_id, self._own()))
        return result.scalar_one_or_none()

    async def list_conversations(self) -> list[ConversationRead]:
        result = await self.session.execute(
            select(ChatConversations).where(self._own())
            .order_by(ChatConversations.updated_at.desc(), ChatConversations.conv_id.desc())
            .limit(CONVERSATIONS_LIST_LIMIT))
        return [conversation_read(row) for row in result.scalars().all()]

    async def create_conversation(
            self, gvdbs_id: int, gllms_id: int, filters: RequestGVDBsRetrFilters | None) -> ConversationRead:
        collection = await self.get_collection(gvdbs_id)
        if not collection:
            raise ChatError("Document collection not found")
        if not await self.get_llm(gllms_id):
            raise ChatError("LLM not found")
        # Keep only filter values that are valid for this collection's schema.
        filters_json = None
        if filters and filters.values:
            try:
                checked = GVDBsRetrFiltersFunctions.check_user_request(filters, collection.gvdbs_retr_filters)
            except Exception:
                checked = None  # the collection defines no filters
            if checked:
                filters_json = json.dumps(checked, indent=1, default=str)
        row = ChatConversations(
            group_id=self.user.group_id, user_id=self.user.user_id, title='',
            gvdbs_id=gvdbs_id, gllms_id=gllms_id, filters_json=filters_json,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return conversation_read(row)

    async def get_conversation(self, conv_id: int) -> ConversationDetail | None:
        row = await self.get_conversation_row(conv_id)
        if not row:
            return None
        result = await self.session.execute(
            select(ChatMessages).where(ChatMessages.conv_id == conv_id).order_by(ChatMessages.seqn))
        messages = [MessageRead.model_validate(m) for m in result.scalars().all()]
        return ConversationDetail(**conversation_read(row).model_dump(), messages=messages)

    async def rename_conversation(self, conv_id: int, title: str) -> ConversationRead | None:
        # updated_at is left alone: renaming must not reorder the sidebar
        result = await self.session.execute(
            update(ChatConversations)
            .where(ChatConversations.conv_id == conv_id, self._own())
            .values(title=title.strip()[:200]))
        await self.session.commit()
        if not result.rowcount:
            return None
        row = await self.get_conversation_row(conv_id)
        return conversation_read(row) if row else None

    async def delete_conversation(self, conv_id: int) -> bool:
        """Hard delete; the messages go with it (ON DELETE CASCADE)."""
        result = await self.session.execute(
            delete(ChatConversations).where(ChatConversations.conv_id == conv_id, self._own()))
        await self.session.commit()
        return bool(result.rowcount)

    async def touch_conversation(self, conv_id: int, **values) -> None:
        await self.session.execute(
            update(ChatConversations)
            .where(ChatConversations.conv_id == conv_id, self._own())
            .values(updated_at=func.now(), **values))
        await self.session.commit()
