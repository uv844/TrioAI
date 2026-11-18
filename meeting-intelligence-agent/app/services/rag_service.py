from pathlib import Path
from functools import lru_cache

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.services.custom_llm import CustomLLM

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPT_PATH = PROJECT_ROOT / "sample_data" / "sample_meeting_transcript.txt"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "meeting_transcripts"

@lru_cache(maxsize=1)
def get_embedder():
    # First run downloads the model from Hugging Face.
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@lru_cache(maxsize=1)
def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def index_sample_transcript():
    if not TRANSCRIPT_PATH.exists():
        raise FileNotFoundError(f"Transcript not found: {TRANSCRIPT_PATH}")

    text = TRANSCRIPT_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    if not chunks:
        raise ValueError("Transcript is empty.")

    embedder = get_embedder()
    vectors = embedder.encode(chunks, normalize_embeddings=True).tolist()
    collection = get_collection()

    # Stable IDs make repeated indexing replace the same sample chunks.
    ids = [f"technova-sample-{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": "sample_meeting_transcript.txt", "meeting": "TechNova Project Planning"}
        for _ in chunks
    ]
    collection.upsert(ids=ids, documents=chunks, embeddings=vectors, metadatas=metadatas)
    return {"indexed_chunks": len(chunks), "collection": COLLECTION_NAME}

def ask_meeting(question: str, top_k: int = 4):
    collection = get_collection()
    if collection.count() == 0:
        raise ValueError("No transcript indexed yet. Call POST /rag/index-sample first.")

    query_vector = get_embedder().encode([question], normalize_embeddings=True).tolist()
    result = collection.query(
        query_embeddings=query_vector,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    if not documents:
        raise ValueError("No relevant transcript chunks were retrieved.")

    context = "\n\n---\n\n".join(
        f"[Source: {meta.get('source', 'meeting transcript')}; distance: {dist:.3f}]\n{doc}"
        for doc, meta, dist in zip(documents, metadatas, distances)
    )
    answer = CustomLLM().generate(question, context)
    return {
        "question": question,
        "answer": answer,
        "retrieved_chunks": [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]
    }
