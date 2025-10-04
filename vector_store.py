from functools import lru_cache
from pathlib import Path
from typing import List, Optional
import shutil

from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Load a better embedding model for improved semantic understanding"""
    # Using a more powerful model for better semantic search
    # Options: "all-MiniLM-L6-v2" (fast), "all-mpnet-base-v2" (better quality)
    return SentenceTransformer(model_name)


def build_vector_store(
    docs: Optional[List] = None,
    *,
    persist_directory: Optional[str] = None,
    collection_name: str = "default",
    recreate: bool = False,
):
    base = _get_model()

    class Embedder:
        def embed_documents(self, texts: List[str]):
            return base.encode(texts).tolist()

        def embed_query(self, text: str):
            return base.encode([text])[0].tolist()

    embeddings = Embedder()
    if persist_directory:
        persist_path = Path(persist_directory)
        if recreate and persist_path.exists():
            shutil.rmtree(persist_path)
        persist_path.mkdir(parents=True, exist_ok=True)
    else:
        persist_path = None

    if docs is None:
        if not persist_path:
            raise ValueError("persist_directory is required when loading an existing vector store")
        return Chroma(
            embedding_function=embeddings,
            persist_directory=str(persist_path),
            collection_name=collection_name,
        )

    return Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(persist_path) if persist_path else None,
        collection_name=collection_name,
    )
