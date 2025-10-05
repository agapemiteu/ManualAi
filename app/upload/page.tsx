"use client";

import React, { ChangeEvent, DragEvent, FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Ban,
  Car,
  CheckCircle,
  FileText,
  Info,
  Loader2,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import clsx from "clsx";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const MAX_FILE_SIZE = 50 * 1024 * 1024;
const ACCEPTED_TYPES = ["application/pdf", "text/html", "text/plain"];
const BRAND_OPTIONS = [
  "Toyota",
  "Honda",
  "Ford",
  "BMW",
  "Mercedes-Benz",
  "Audi",
  "VW",
  "Nissan",
  "Hyundai",
  "Kia",
  "Mazda",
  "Subaru",
  "Lexus",
  "Tesla",
  "Volvo",
  "Jeep",
  "MG",
  "Other",
];

type UploadState = "idle" | "uploading" | "processing" | "ready" | "failed";

interface ManualStatus {
  manual_id: string;
  status: "processing" | "ready" | "failed";
  filename?: string;
  brand?: string | null;
  model?: string | null;
  year?: string | null;
  error?: string | null;
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "")
    .slice(0, 80) || "manual-" + Date.now();
}

function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [manualId, setManualId] = useState("");
  const [brand, setBrand] = useState<string>(BRAND_OPTIONS[0]);
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState<number>(0);
  const [message, setMessage] = useState<string | null>(null);
  const [manualStatus, setManualStatus] = useState<ManualStatus | null>(null);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  const handleFileSelection = useCallback(
    (selectedFile: File | null) => {
      if (!selectedFile) {
        setFile(null);
        setManualId("");
        return;
      }

      if (!ACCEPTED_TYPES.includes(selectedFile.type)) {
        setMessage("Unsupported file type. Please upload a PDF, HTML, or TXT file.");
        return;
      }

      if (selectedFile.size > MAX_FILE_SIZE) {
        setMessage(`File is too large. Maximum allowed size is ${formatBytes(MAX_FILE_SIZE)}.`);
        return;
      }

      setFile(selectedFile);
      setManualId(slugify(selectedFile.name.replace(/\.[^/.]+$/, "")));
      setMessage(null);
      setProgress(0);
      setUploadState("idle");
      setManualStatus(null);
      setReplaceExisting(false);
    },
    []
  );

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    const droppedFile = event.dataTransfer?.files?.[0];
    handleFileSelection(droppedFile ?? null);
  };

  const onDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const onFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    handleFileSelection(selectedFile);
  };

  const startStatusPolling = useCallback((id: string) => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    const poll = async () => {
      try {
        const response = await fetch(`${API_URL}/api/manuals/${encodeURIComponent(id)}`);
        if (!response.ok) {
          throw new Error(`Status request failed with ${response.status}`);
        }
        const data = (await response.json()) as ManualStatus;
        setManualStatus(data);

        if (data.status === "ready") {
          setUploadState("ready");
          setMessage(`Manual processed successfully for ${data.brand ?? ""}`.trim());
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
          }
        } else if (data.status === "failed") {
          setUploadState("failed");
          setMessage(data.error ? `Manual ingestion failed: ${data.error}` : "Manual ingestion failed. Please check the file and try again.");
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
          }
        }
      } catch (error) {
        console.error(error);
        setUploadState("failed");
        setMessage("Unable to retrieve manual status. Please try again later.");
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
        }
      }
    };

    pollingRef.current = setInterval(poll, 2000);
    poll();
  }, []);

  const cancelManual = useCallback(async () => {
    if (!manualStatus) {
      return;
    }
    setIsCancelling(true);
    try {
      const response = await fetch(`${API_URL}/api/manuals/${encodeURIComponent(manualStatus.manual_id)}/cancel`, { method: "POST" });
      if (!response.ok) {
        throw new Error(`Cancel request failed with ${response.status}`);
      }
      const data = (await response.json()) as ManualStatus;
      setManualStatus(data);
      setUploadState(data.status === "ready" ? "ready" : data.status === "failed" ? "failed" : "processing");
      setMessage(data.status === "failed" ? "Ingestion cancelled. Manual marked as failed." : "Cancellation requested. Manual will stop processing shortly.");
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      startStatusPolling(manualStatus.manual_id);
    } catch (error) {
      console.error(error);
      const detail = error instanceof Error ? error.message : "";
      setMessage(detail || "Failed to cancel ingestion. Please try again.");
    } finally {
      setIsCancelling(false);
    }
  }, [manualStatus, startStatusPolling]);

  const deleteManual = useCallback(async () => {
    if (!manualStatus) {
      return;
    }
    setIsDeleting(true);
    try {
      const response = await fetch(`${API_URL}/api/manuals/${encodeURIComponent(manualStatus.manual_id)}`, { method: "DELETE" });
      if (!response.ok) {
        throw new Error(`Delete request failed with ${response.status}`);
      }
      setMessage("Manual deleted successfully.");
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      setManualStatus(null);
      setUploadState("idle");
      setProgress(0);
    } catch (error) {
      console.error(error);
      const detail = error instanceof Error ? error.message : "";
      setMessage(detail || "Failed to delete manual. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  }, [manualStatus]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setMessage("Please choose a file to upload.");
      return;
    }
    if (!manualId.trim()) {
      setMessage("Manual ID is required.");
      return;
    }

    const formData = new FormData();
    formData.append("manual_id", manualId.trim());
    formData.append("brand", brand);
    if (model.trim()) {
      formData.append("model", model.trim());
    }
    if (year.trim()) {
      formData.append("year", year.trim());
    }
    formData.append("file", file);
    formData.append("replace", replaceExisting ? "true" : "false");

    setUploadState("uploading");
    setProgress(0);
    setMessage(null);
    setManualStatus(null);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }

    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `${API_URL}/api/manuals`);
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const value = Math.round((event.loaded / event.total) * 100);
            setProgress(value);
          }
        };
        xhr.onload = () => {
          if (xhr.status === 202) {
            resolve();
          } else {
            let detail: string | undefined;
            try {
              const body = xhr.responseText ? JSON.parse(xhr.responseText) : null;
              detail = typeof body?.detail === 'string' ? body.detail : undefined;
            } catch {}
            reject(new Error(detail || `Upload failed with status ${xhr.status}`));
          }
        };
        xhr.onerror = () => {
          let detail: string | undefined;
          try {
            const body = xhr.responseText ? JSON.parse(xhr.responseText) : null;
            detail = typeof body?.detail === 'string' ? body.detail : undefined;
          } catch {}
          reject(new Error(detail || "Upload failed"));
        };
        xhr.send(formData);
      });

      setUploadState("processing");
      startStatusPolling(manualId.trim());
    } catch (error) {
      console.error(error);
      setUploadState("failed");
      const detail = error instanceof Error ? error.message : "";
      setMessage(detail || "Upload failed. Please try again.");
    }
  };

  const removeFile = () => {
    setFile(null);
    setManualId("");
    setProgress(0);
    setUploadState("idle");
    setMessage(null);
    setManualStatus(null);
    setReplaceExisting(false);
  };

  const statusIcon = useMemo(() => {
    if (uploadState === "ready") {
      return <CheckCircle className="h-5 w-5 text-emerald-400" />;
    }
    if (uploadState === "failed") {
      return <AlertCircle className="h-5 w-5 text-red-400" />;
    }
    if (uploadState === "processing" || uploadState === "uploading") {
      return <Loader2 className="h-5 w-5 animate-spin text-sky-400" />;
    }
    return null;
  }, [uploadState]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 py-10">
      <div className="mx-auto max-w-3xl px-4">
        <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-950/60 p-8 shadow-xl shadow-slate-900/40">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800/80">
              <Upload className="h-6 w-6 text-sky-400" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-white">Upload Manual</h1>
              <p className="text-sm text-slate-400">
                Upload PDF, HTML, or TXT manuals up to 50MB. Provide brand details to keep manuals organised.
              </p>
            </div>
          </div>
          <div className="mt-5 flex items-start gap-2 rounded-lg border border-slate-800 bg-slate-900/80 p-3 text-sm text-slate-300">
            <Info className="mt-0.5 h-4 w-4 text-sky-400" />
            <p>
              Manual IDs are auto-generated from filenames. You can adjust them before uploading. Once uploaded, the manual
              will be processed and available for chat queries.
            </p>
          </div>
        </div>

        <form onSubmit={onSubmit} className="space-y-6">
          <div
            onDrop={onDrop}
            onDragOver={onDragOver}
            className={clsx(
              "flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed bg-slate-950/60 p-8 transition hover:border-sky-500/60",
              file ? "border-sky-500/80" : "border-slate-800"
            )}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf,.html,.txt"
              className="hidden"
              onChange={onFileInputChange}
            />
            {file ? (
              <div className="flex w-full flex-col items-center gap-3 text-center">
                <FileText className="h-10 w-10 text-sky-400" />
                <div>
                  <p className="font-medium text-white">{file.name}</p>
                  <p className="text-xs text-slate-400">{formatBytes(file.size)}</p>
                </div>
                <button
                  type="button"
                  onClick={removeFile}
                  className="inline-flex items-center gap-1 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 transition hover:bg-slate-700"
                >
                  <X className="h-4 w-4" /> Remove file
                </button>
              </div>
            ) : (
              <label htmlFor="file-input" className="flex flex-col items-center gap-3 text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-800/80">
                  <Upload className="h-6 w-6 text-sky-400" />
                </div>
                <div>
                  <p className="font-medium text-white">Drop your manual here or click to browse</p>
                  <p className="text-xs text-slate-400">PDF, HTML, or TXT up to 50MB</p>
                </div>
              </label>
            )}
          </div>

          <div className="grid gap-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-6 md:grid-cols-2">
            <div className="md:col-span-2">
              <label htmlFor="manual_id" className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-200">
                <FileText className="h-4 w-4 text-sky-400" /> Manual ID
              </label>
              <input
                id="manual_id"
                value={manualId}
                onChange={(event) => setManualId(event.target.value)}
                placeholder="auto-generated-manual-id"
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label htmlFor="brand" className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-200">
                <Car className="h-4 w-4 text-sky-400" /> Brand
              </label>
              <select
                id="brand"
                value={brand}
                onChange={(event) => setBrand(event.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none"
                required
              >
                {BRAND_OPTIONS.map((option) => (
                  <option key={option} value={option} className="bg-slate-900 text-slate-100">
                    {option}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="model" className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-200">
                Model (optional)
              </label>
              <input
                id="model"
                value={model}
                onChange={(event) => setModel(event.target.value)}
                placeholder="e.g. Corolla"
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none"
              />
            </div>

            <div>
              <label htmlFor="year" className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-200">
                Year (optional)
              </label>
              <input
                id="year"
                value={year}
                onChange={(event) => setYear(event.target.value)}
                placeholder="e.g. 2021"
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
            <div className="mb-4 flex items-center gap-2">
              <input
                id="replace"
                type="checkbox"
                className="h-4 w-4 rounded border border-slate-700 bg-slate-900 text-sky-500 focus:ring-sky-500"
                checked={replaceExisting}
                onChange={(event) => setReplaceExisting(event.target.checked)}
              />
              <label htmlFor="replace" className="text-sm text-slate-300">
                Replace existing manual with the same ID
              </label>
            </div>
            <button
              type="submit"
              disabled={!file || uploadState === "uploading" || uploadState === "processing"}
              className={clsx(
                "flex w-full items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-3 text-sm font-semibold tracking-wide text-white transition",
                uploadState === "uploading" || uploadState === "processing"
                  ? "cursor-not-allowed opacity-70"
                  : "hover:bg-sky-500"
              )}
            >
              {uploadState === "uploading" || uploadState === "processing" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              {uploadState === "uploading"
                ? "Uploading..."
                : uploadState === "processing"
                ? "Processing..."
                : "Upload Manual"}
            </button>

            {uploadState === "uploading" && (
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Uploading file</span>
                  <span>{progress}%</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-sky-500 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {statusIcon && (
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-300">
                {statusIcon}
                <span>
                  {uploadState === "processing"
                    ? "Manual is being ingested..."
                    : uploadState === "ready"
                    ? "Manual ingestion complete."
                    : uploadState === "failed"
                    ? "Manual ingestion failed."
                    : null}
                </span>
              </div>
            )}

            {message && (
              <div className="mt-4 flex items-start gap-2 rounded-lg border border-slate-800 bg-slate-900/80 p-3 text-sm text-slate-200">
                <AlertCircle className="mt-0.5 h-4 w-4 text-amber-400" />
                <p>{message}</p>
              </div>
            )}

            {manualStatus && (
              <div className="mt-4 space-y-1 rounded-lg border border-slate-800 bg-slate-900/80 p-3 text-sm text-slate-300">
                <p className="font-medium text-slate-100">Manual Details</p>
                <p>ID: {manualStatus.manual_id}</p>
                {manualStatus.brand && <p>Brand: {manualStatus.brand}</p>}
                {manualStatus.model && <p>Model: {manualStatus.model}</p>}
                {manualStatus.year && <p>Year: {manualStatus.year}</p>}
                <p>Status: {manualStatus.status}</p>
                {manualStatus.error && (
                  <p className="text-amber-300">Error: {manualStatus.error}</p>
                )}
              <div className="mt-3 flex flex-wrap gap-2">
                {manualStatus.status === "processing" && (
                  <button
                    type="button"
                    onClick={cancelManual}
                    disabled={isCancelling}
                    className={clsx("inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-200 transition hover:border-sky-500 hover:text-sky-300", isCancelling && "cursor-not-allowed opacity-70")}
                  >
                    <Ban className="h-4 w-4 text-sky-400" /> {isCancelling ? "Cancelling..." : "Cancel ingestion"}
                  </button>
                )}
                <button
                  type="button"
                  onClick={deleteManual}
                  disabled={isDeleting}
                  className={clsx("inline-flex items-center gap-2 rounded-lg border border-red-500/50 bg-red-500/10 px-3 py-2 text-xs font-medium text-red-200 transition hover:bg-red-500/20", isDeleting && "cursor-not-allowed opacity-70")}
                >
                  <Trash2 className="h-4 w-4" /> {isDeleting ? "Deleting..." : "Delete manual"}
                </button>
              </div>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadPage;
