"""Query the local Chroma RAG corpus with optional questionnaire metadata filters."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.rag_ranking import rank_retrieved_chunks  # noqa: E402

VECTOR_DIR = ROOT / "data" / "silver" / "vector_store" / "chroma"
COLLECTION_NAME = "mcgill_care_compass_rag"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NEED_TYPE_TO_BOOL = {
    "eligibility": "has_eligibility",
    "required_docs": "has_required_docs",
    "costs_coverage": "has_costs_coverage",
    "contact": "has_contact_info",
    "location": "has_location",
    "deadlines": "has_deadlines",
    "booking_steps": "has_booking_steps",
    "emergency_info": "has_emergency_info",
    "emergency": "has_emergency_info",
    "general_navigation": "",
}


def where_filter(args: argparse.Namespace) -> dict:
    filters = []
    for option, field in [
        (args.category_id, "category_id"),
        (args.student_type, "student_type"),
        (args.jurisdiction, "jurisdiction"),
        (args.language, "language"),
        (args.risk_level, "risk_level"),
    ]:
        if option:
            filters.append({field: option})
    if args.need_type:
        bool_field = NEED_TYPE_TO_BOOL.get(args.need_type)
        if bool_field:
            filters.append({bool_field: True})
    if not filters:
        return {}
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local RAG vector corpus.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--category-id")
    parser.add_argument("--need-type")
    parser.add_argument("--student-type")
    parser.add_argument("--jurisdiction")
    parser.add_argument("--language")
    parser.add_argument("--risk-level")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    model = SentenceTransformer(args.embedding_model)
    query_embedding = model.encode([args.query], normalize_embeddings=True)[0].tolist()
    total_chunks = collection.count()
    if total_chunks == 0:
        print("No chunks are available in the vector store.")
        return
    candidate_limit = min(total_chunks, max(args.limit * 4, args.limit))
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_limit,
        where=where_filter(args) or None,
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    if not documents:
        print("No chunks matched the query and filters.")
        return
    candidates = [
        {"document": document, "metadata": metadata, "distance": distance}
        for document, metadata, distance in zip(documents, metadatas, distances, strict=False)
    ]
    for index, candidate in enumerate(rank_retrieved_chunks(candidates)[: args.limit], start=1):
        document = candidate["document"]
        metadata = candidate["metadata"]
        distance = candidate["distance"]
        print(f"\n[{index}] distance={distance:.4f}")
        print(f"URL: {metadata.get('canonical_url')}")
        print(f"Section: {metadata.get('heading_path')}")
        print(
            "Source: "
            f"{metadata.get('source_group')} rank={metadata.get('source_priority_rank')} "
            f"freshness={metadata.get('freshness_score')}"
        )
        print(
            "Terms: "
            f"{metadata.get('licence_or_terms')} | {metadata.get('terms_url')}"
        )
        print(f"Category: {metadata.get('category_id')} | tags: {metadata.get('info_type_tags')}")
        print(document[:700])


if __name__ == "__main__":
    main()
