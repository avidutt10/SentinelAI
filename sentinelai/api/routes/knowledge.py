from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from sentinelai.api.dependencies import get_db_session, require_api_key
from sentinelai.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from sentinelai.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"], dependencies=[Depends(require_api_key)])


@router.post("/ingest", response_model=KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def ingest_document(payload: KnowledgeDocumentCreate, db: Session = Depends(get_db_session)) -> KnowledgeDocumentRead:
    document = KnowledgeService(db).ingest(payload)
    return KnowledgeDocumentRead(
        id=document.id,
        doc_id=document.doc_id,
        title=document.title,
        doc_type=document.doc_type,
        tags=document.tags,
        content=document.content,
        source=document.source,
        metadata=document.metadata_json,
        created_at=document.created_at,
    )


@router.post("/search", response_model=list[KnowledgeSearchResult])
def search_knowledge(payload: KnowledgeSearchRequest, db: Session = Depends(get_db_session)) -> list[KnowledgeSearchResult]:
    return KnowledgeService(db).retrieve(query=payload.query, top_k=payload.top_k)
