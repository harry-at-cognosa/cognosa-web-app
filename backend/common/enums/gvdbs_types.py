from typing import Literal

class GVDBsTypes:
    CHROMA = 'chroma'
    QDRANT = 'qdrant'
    PGVECTOR = 'pgvector'

type_GVDBsTypes = Literal['chroma', 'qdrant', 'pgvector']
