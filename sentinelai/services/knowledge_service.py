from __future__ import annotations

import math
import re
from collections import Counter

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinelai.core.config import get_settings
from sentinelai.models.db import KnowledgeDocument
from sentinelai.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeSearchResult

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def text_to_counter(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    if numerator == 0:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class KnowledgeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def ingest(self, payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
        existing = self.db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.doc_id == payload.doc_id))
        if existing:
            existing.title = payload.title
            existing.doc_type = payload.doc_type
            existing.tags = payload.tags
            existing.content = payload.content
            existing.source = payload.source
            existing.metadata_json = payload.metadata
            document = existing
        else:
            document = KnowledgeDocument(
                doc_id=payload.doc_id,
                title=payload.title,
                doc_type=payload.doc_type,
                tags=payload.tags,
                content=payload.content,
                source=payload.source,
                metadata_json=payload.metadata,
            )
            self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        self._upsert_vector(document)
        return document

    def retrieve(self, query: str, top_k: int) -> list[KnowledgeSearchResult]:
        if self.settings.vector_backend == "qdrant":
            results = self._retrieve_qdrant(query, top_k)
            if results:
                return results
        documents = self.db.scalars(select(KnowledgeDocument)).all()
        query_counter = text_to_counter(query)
        scored = []
        for doc in documents:
            searchable = " ".join([doc.title, doc.content, " ".join(doc.tags)])
            score = cosine_similarity(query_counter, text_to_counter(searchable))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            KnowledgeSearchResult(
                doc_id=doc.doc_id,
                title=doc.title,
                doc_type=doc.doc_type,
                score=round(score, 4),
                tags=doc.tags,
                excerpt=doc.content[:240],
            )
            for score, doc in scored[:top_k]
        ]

    def _qdrant_client(self) -> QdrantClient | None:
        try:
            return QdrantClient(url=self.settings.qdrant_url)
        except Exception:
            return None

    def _upsert_vector(self, document: KnowledgeDocument) -> None:
        if self.settings.vector_backend != "qdrant":
            return
        client = self._qdrant_client()
        if client is None:
            return
        vector = self._dense_projection(document.title + " " + document.content)
        try:
            client.get_collection(self.settings.qdrant_collection)
        except UnexpectedResponse:
            client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
            )
        client.upsert(
            collection_name=self.settings.qdrant_collection,
            points=[
                PointStruct(
                    id=document.id,
                    vector=vector,
                    payload={
                        "doc_id": document.doc_id,
                        "title": document.title,
                        "doc_type": document.doc_type,
                        "tags": document.tags,
                        "content": document.content,
                    },
                )
            ],
        )

    def _retrieve_qdrant(self, query: str, top_k: int) -> list[KnowledgeSearchResult]:
        client = self._qdrant_client()
        if client is None:
            return []
        try:
            search = client.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=self._dense_projection(query),
                limit=top_k,
            )
        except Exception:
            return []
        return [
            KnowledgeSearchResult(
                doc_id=item.payload["doc_id"],
                title=item.payload["title"],
                doc_type=item.payload["doc_type"],
                score=round(float(item.score), 4),
                tags=item.payload["tags"],
                excerpt=str(item.payload["content"])[:240],
            )
            for item in search
        ]

    def _dense_projection(self, text: str, size: int = 64) -> list[float]:
        vector = [0.0] * size
        for token, count in text_to_counter(text).items():
            index = hash(token) % size
            vector[index] += float(count)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
