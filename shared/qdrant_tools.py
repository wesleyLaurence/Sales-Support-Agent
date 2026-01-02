from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import PointStruct, VectorParams, Distance
except ImportError:  # pragma: no cover - optional dependency
    QdrantClient = None
    PointStruct = None
    VectorParams = None
    Distance = None


DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "driftdesk_products")
DEFAULT_DIM = int(os.getenv("QDRANT_VECTOR_DIM", "128"))
DEFAULT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


def embed_text(text: str, dim: int = DEFAULT_DIM) -> List[float]:
    """Deterministic hash-based embedding for demos."""
    vector = [0.0] * dim
    for idx, byte in enumerate(text.encode("utf-8")):
        vector[(byte + idx) % dim] += 1.0
    norm = math.sqrt(sum(val * val for val in vector)) or 1.0
    return [val / norm for val in vector]


def _get_client() -> QdrantClient:
    if QdrantClient is None:
        raise RuntimeError("qdrant-client not installed")
    return QdrantClient(url=DEFAULT_URL)


def search_product_vectors(query: str, limit: int = 3) -> Dict[str, Any]:
    """Search product info stored in Qdrant."""
    try:
        client = _get_client()
    except RuntimeError as exc:
        return {"error": str(exc)}

    embedding = embed_text(query)
    results = client.search(
        collection_name=DEFAULT_COLLECTION,
        query_vector=embedding,
        limit=max(int(limit), 1),
    )

    matches = []
    for result in results:
        payload = result.payload or {}
        matches.append(
            {
                "score": result.score,
                "sku": payload.get("sku"),
                "name": payload.get("name"),
                "description": payload.get("description"),
                "category": payload.get("category"),
            }
        )

    return {"matches": matches, "count": len(matches)}


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="search_product_vectors",
        description="Search product info stored in Qdrant by semantic similarity.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    )
]


def seed_products(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Seed a Qdrant collection with product embeddings."""
    if QdrantClient is None:
        return {"error": "qdrant-client not installed"}

    client = _get_client()
    if not client.collection_exists(DEFAULT_COLLECTION):
        client.create_collection(
            collection_name=DEFAULT_COLLECTION,
            vectors_config=VectorParams(size=DEFAULT_DIM, distance=Distance.COSINE),
        )

    points = []
    for index, product in enumerate(products, start=1):
        text = " ".join(
            [
                product.get("name", ""),
                product.get("description", ""),
                " ".join(product.get("tags", [])),
            ]
        )
        point_id = hashlib.sha1(product["sku"].encode("utf-8")).hexdigest()[:8]
        points.append(
            PointStruct(
                id=point_id,
                vector=embed_text(text),
                payload=product,
            )
        )

    client.upsert(collection_name=DEFAULT_COLLECTION, points=points)
    return {"status": "seeded", "count": len(points)}
