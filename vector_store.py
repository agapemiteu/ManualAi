import os
import tempfile
from pathlib import Path

# CRITICAL: Set HuggingFace cache BEFORE any imports
# This must happen before sentence_transformers or any HF library imports
_HF_CACHE = Path(os.getenv("HF_HOME", tempfile.gettempdir() + "/manualai_hf_cache"))
try:
    _HF_CACHE.mkdir(parents=True, exist_ok=True)
    # Test write permissions
    test_file = _HF_CACHE / ".write_test"
    test_file.touch()
    test_file.unlink()
except:
    # Fallback: tempfile.mkdtemp() ALWAYS works
    _HF_CACHE = Path(tempfile.mkdtemp(prefix="manualai_hf_cache_"))

# Set ALL HuggingFace cache env vars
os.environ["HF_HOME"] = str(_HF_CACHE)
os.environ["TRANSFORMERS_CACHE"] = str(_HF_CACHE)
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(_HF_CACHE)
os.environ["HUGGINGFACE_HUB_CACHE"] = str(_HF_CACHE)

# NOW import HuggingFace libraries - they'll use our cache
from functools import lru_cache
from typing import List, Optional
import shutil

from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Load a better embedding model for improved semantic understanding"""
    # Using a more powerful model for better semantic search
    # Options: "all-MiniLM-L6-v2" (fast), "all-mpnet-base-v2" (better quality)
    return SentenceTransformer(model_name, cache_folder=str(_HF_CACHE))


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
