from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
import shutil
from threading import Lock
from typing import Dict, List, Optional
from uuid import uuid4

from dotenv import find_dotenv, load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Lazy imports - only load when needed to speed up startup
# from document_loader import load_manual
# from rag_chain import make_rag_chain
# from vector_store import build_vector_store

# Load environment variables from .env.local if present
dotenv_path = find_dotenv(".env.local")
load_dotenv(dotenv_path, override=True)

logger = logging.getLogger(__name__)

# Lazy loading functions
def load_manual(path):
    from document_loader import load_manual as _load_manual
    return _load_manual(path)

def make_rag_chain(retriever):
    from rag_chain import make_rag_chain as _make_rag_chain
    return _make_rag_chain(retriever)

def build_vector_store(*args, **kwargs):
    from vector_store import build_vector_store as _build_vector_store
    return _build_vector_store(*args, **kwargs)

DEFAULT_MANUAL_BRAND = os.getenv("DEFAULT_MANUAL_BRAND", "default")
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOW_ORIGINS.split(",") if origin.strip()]


class ManualStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass
class ManualMetadata:
    manual_id: str
    source_path: str
    persist_path: str
    filename: str
    brand: str
    model: Optional[str] = None
    year: Optional[str] = None


@dataclass
class ManualEntry:
    metadata: ManualMetadata
    chain: object
    vector_store: object


class ManualNotReadyError(Exception):
    def __init__(self, manual_id: str, status: ManualStatus) -> None:
        super().__init__(f"Manual '{manual_id}' is {status.value}.")
        self.manual_id = manual_id
        self.status = status


class ManualManager:
    def __init__(
        self,
        default_manual_path: Path,
        upload_dir: Path,
        storage_dir: Path,
        default_manual_id: str = "default",
    ) -> None:
        self._lock = Lock()
        self._entries: Dict[str, ManualEntry] = {}
        self._metas: Dict[str, ManualMetadata] = {}
        self._statuses: Dict[str, ManualStatus] = {}
        self.default_manual_id = default_manual_id
        self.upload_dir = upload_dir
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.storage_dir / "manifest.json"

        self._load_manifest()

        default_status = self._statuses.get(default_manual_id)
        if default_status is not ManualStatus.READY:
            meta = self._metas.get(default_manual_id) or ManualMetadata(
                manual_id=default_manual_id,
                source_path=str(default_manual_path),
                persist_path=str(self._persist_path(default_manual_id)),
                filename=Path(default_manual_path).name,
                brand=DEFAULT_MANUAL_BRAND,
            )
            self._metas[default_manual_id] = meta
            self._statuses[default_manual_id] = ManualStatus.PROCESSING
            self._ingest_manual(meta, recreate=True)

    def _persist_path(self, manual_id: str) -> Path:
        return self.storage_dir / manual_id / "vector_store"

    def _load_manifest(self) -> None:
        if not self.manifest_path.exists():
            return
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Unable to read manual manifest: %s", exc)
            return

        for item in data.get("manuals", []):
            try:
                item.setdefault("brand", DEFAULT_MANUAL_BRAND)
                item.setdefault("model", None)
                item.setdefault("year", None)
                meta = ManualMetadata(**item)
            except TypeError:  # pragma: no cover - defensive
                logger.warning("Skipping malformed manifest entry: %s", item)
                continue

            try:
                vector_store = build_vector_store(
                    docs=None,
                    persist_directory=meta.persist_path,
                    collection_name=meta.manual_id,
                )
                entry = ManualEntry(
                    metadata=meta,
                    vector_store=vector_store,
                    chain=make_rag_chain(vector_store.as_retriever()),
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to hydrate manual '%s': %s", meta.manual_id, exc)
                self._metas[meta.manual_id] = meta
                self._statuses[meta.manual_id] = ManualStatus.FAILED
                continue

            self._metas[meta.manual_id] = meta
            self._entries[meta.manual_id] = entry
            self._statuses[meta.manual_id] = ManualStatus.READY

    def _save_manifest(self) -> None:
        with self._lock:
            ready_entries = [asdict(entry.metadata) for entry in self._entries.values()]
        payload = json.dumps({"manuals": ready_entries}, indent=2)
        self.manifest_path.write_text(payload, encoding="utf-8")

    def remove_manual(self, manual_id: str) -> ManualStatus:
        with self._lock:
            status = self._statuses.get(manual_id)
            if status is None:
                raise KeyError(manual_id)
            if status is ManualStatus.PROCESSING:
                raise ValueError(f"Manual '{manual_id}' is still processing.")
            meta = self._metas.pop(manual_id, None)
            self._entries.pop(manual_id, None)
            self._statuses.pop(manual_id, None)

        if meta:
            persist_root = Path(meta.persist_path).parent
            shutil.rmtree(persist_root, ignore_errors=True)
        upload_path = self.upload_dir / manual_id
        shutil.rmtree(upload_path, ignore_errors=True)
        self._save_manifest()
        return status

    def register_manual(
        self,
        manual_id: str,
        manual_path: Path,
        filename: str,
        brand: str,
        model: Optional[str] = None,
        year: Optional[str] = None,
        *,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> ManualStatus:
        manual_path = manual_path.resolve()
        persist_path = self._persist_path(manual_id)

        with self._lock:
            current_status = self._statuses.get(manual_id)
            if current_status is ManualStatus.PROCESSING:
                raise ValueError(f"Manual '{manual_id}' is still processing.")
            if current_status is ManualStatus.READY:
                raise ValueError(f"Manual '{manual_id}' already exists.")

            brand_value = (brand or "").strip() or DEFAULT_MANUAL_BRAND
            model_value = (model or "").strip() or None
            year_value = (year or "").strip() or None

            meta = ManualMetadata(
                manual_id=manual_id,
                source_path=str(manual_path),
                persist_path=str(persist_path),
                filename=filename,
                brand=brand_value,
                model=model_value,
                year=year_value,
            )
            self._metas[manual_id] = meta
            self._statuses[manual_id] = ManualStatus.PROCESSING

        if background_tasks is not None:
            background_tasks.add_task(self._background_ingest, meta)
        else:
            self._ingest_manual(meta, recreate=True)

        return ManualStatus.PROCESSING

    def _background_ingest(self, meta: ManualMetadata) -> None:
        try:
            self._ingest_manual(meta, recreate=True)
        except Exception:  # pragma: no cover - logged upstream
            logger.exception("Background ingestion failed for manual '%s'", meta.manual_id)

    def _ingest_manual(self, meta: ManualMetadata, recreate: bool = False) -> None:
        try:
            docs = load_manual(meta.source_path)
            if not docs:
                raise ValueError("No readable content found in the supplied manual.")

            persist_path = Path(meta.persist_path)
            persist_path.parent.mkdir(parents=True, exist_ok=True)

            vector_store = build_vector_store(
                docs,
                persist_directory=str(persist_path),
                collection_name=meta.manual_id,
                recreate=recreate,
            )
            entry = ManualEntry(
                metadata=meta,
                vector_store=vector_store,
                chain=make_rag_chain(vector_store.as_retriever()),
            )

            with self._lock:
                self._entries[meta.manual_id] = entry
                self._statuses[meta.manual_id] = ManualStatus.READY

            self._save_manifest()
        except Exception:
            with self._lock:
                self._statuses[meta.manual_id] = ManualStatus.FAILED
            raise

    def get_chain(self, manual_id: Optional[str]) -> object:
        target_id = manual_id or self.default_manual_id
        with self._lock:
            status = self._statuses.get(target_id)
            if status is None:
                raise KeyError(target_id)
            if status is not ManualStatus.READY:
                raise ManualNotReadyError(target_id, status)
            entry = self._entries[target_id]
        return entry.chain

    def get_status(self, manual_id: str) -> ManualStatus:
        with self._lock:
            status = self._statuses.get(manual_id)
            if status is None:
                raise KeyError(manual_id)
            return status

    def get_manual_info(self, manual_id: str) -> Dict[str, object]:
        with self._lock:
            meta = self._metas.get(manual_id)
            status = self._statuses.get(manual_id)
        if meta is None or status is None:
            raise KeyError(manual_id)
        return {
            "manual_id": manual_id,
            "status": status,
            "filename": meta.filename,
            "brand": meta.brand,
            "model": meta.model,
            "year": meta.year,
        }

    def list_manuals(self) -> List[Dict[str, object]]:
        with self._lock:
            manual_ids = sorted(self._metas.keys())
            infos = []
            for manual_id in manual_ids:
                meta = self._metas[manual_id]
                status = self._statuses.get(manual_id, ManualStatus.PROCESSING)
                infos.append(
                    {
                        "manual_id": manual_id,
                        "status": status,
                        "filename": meta.filename,
                        "brand": meta.brand,
                        "model": meta.model,
                        "year": meta.year,
                    }
                )
            return infos


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint - responds immediately
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Welcome to ManualAi API!", "status": "running"}


DOC_PATH = Path(os.getenv("MANUAL_PATH", "../data/README.md")).resolve()  # Use README instead of HTML
UPLOAD_DIR = Path(os.getenv("MANUAL_UPLOAD_DIR", Path("../data/uploads"))).resolve()
STORAGE_DIR = Path(os.getenv("MANUAL_STORAGE_DIR", Path("../data/manual_store"))).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Skip default manual loading - let users upload their own
manual_manager = ManualManager.__new__(ManualManager)
manual_manager._lock = Lock()
manual_manager._entries = {}
manual_manager._metas = {}
manual_manager._statuses = {}
manual_manager.default_manual_id = "default"
manual_manager.upload_dir = UPLOAD_DIR
manual_manager.storage_dir = STORAGE_DIR
manual_manager.storage_dir.mkdir(parents=True, exist_ok=True)
manual_manager.manifest_path = manual_manager.storage_dir / "manifest.json"
manual_manager._load_manifest()


class QueryRequest(BaseModel):
    question: str
    manual_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str


class ManualInfo(BaseModel):
    manual_id: str
    status: ManualStatus
    filename: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None


class ManualListResponse(BaseModel):
    manuals: List[ManualInfo]


class ManualUploadResponse(ManualInfo):
    pass


@app.post("/api/chat", response_model=QueryResponse)
async def chat(req: QueryRequest) -> QueryResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    try:
        chain = manual_manager.get_chain(req.manual_id)
    except ManualNotReadyError as exc:
        raise HTTPException(status_code=409, detail=f"Manual '{exc.manual_id}' is {exc.status.value}.") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Manual '{exc.args[0]}' not found.") from exc

    resp = chain.invoke(req.question)
    return QueryResponse(answer=resp.content)


@app.get("/api/manuals", response_model=ManualListResponse)
async def list_manuals() -> ManualListResponse:
    infos = [ManualInfo(**info) for info in manual_manager.list_manuals()]
    return ManualListResponse(manuals=infos)


@app.get("/api/manuals/{manual_id}", response_model=ManualInfo)
async def get_manual(manual_id: str) -> ManualInfo:
    try:
        info = manual_manager.get_manual_info(manual_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Manual '{exc.args[0]}' not found.") from exc
    return ManualInfo(**info)


@app.post("/api/manuals", response_model=ManualUploadResponse, status_code=202)
async def upload_manual(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    manual_id: Optional[str] = Form(None),
    brand: str = Form(...),
    model: Optional[str] = Form(None),
    year: Optional[str] = Form(None),
    replace: bool = Form(False),
) -> ManualUploadResponse:
    manual_identifier = manual_id or f"manual-{uuid4().hex[:8]}"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if replace:
        if manual_id is None:
            raise HTTPException(status_code=400, detail="Manual ID is required when replace is enabled.")
        try:
            manual_manager.remove_manual(manual_identifier)
        except KeyError:
            pass
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    dest_dir = UPLOAD_DIR / manual_identifier
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename
    dest_path.write_bytes(content)

    try:
        manual_manager.register_manual(
            manual_identifier,
            dest_path,
            file.filename,
            brand,
            model,
            year,
            background_tasks=background_tasks,
        )
    except ValueError as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to ingest manual.") from exc

    info = manual_manager.get_manual_info(manual_identifier)
    return ManualUploadResponse(**info)


@app.delete("/api/manuals/{manual_id}", status_code=204)
async def delete_manual(manual_id: str) -> Response:
    try:
        manual_manager.remove_manual(manual_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Manual '{exc.args[0]}' not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=204)
