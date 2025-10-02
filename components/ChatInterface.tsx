"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Loader2, Send, RefreshCcw } from "lucide-react";
import clsx from "clsx";
import MessageBubble, { ChatMessage } from "./MessageBubble";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type ManualStatus = "processing" | "ready" | "failed";

interface Manual {
  manual_id: string;
  status: ManualStatus;
  filename?: string;
  brand?: string | null;
  model?: string | null;
  year?: string | null;
}

interface ManualListResponse {
  manuals: Manual[];
}

const deriveSuggestions = (manual?: Manual | null): string[] => {
  if (!manual) {
    return [
      "What does the check engine light mean?",
      "How often should I service my car?",
      "What safety features does this car have?",
    ];
  }

  const tags: string[] = [];
  if (manual.brand) {
    tags.push(manual.brand.toLowerCase());
  }
  if (manual.model) {
    tags.push(manual.model.toLowerCase());
  }

  if (tags.some((tag) => tag.includes("lexus") || tag.includes("toyota"))) {
    return [
      "What does the brake warning light mean?",
      "How do I use the safety system features?",
      "What is the recommended service interval?",
    ];
  }

  if (tags.some((tag) => tag.includes("tesla"))) {
    return [
      "How do I find the nearest charging station?",
      "What does the autopilot warning mean?",
      "How can I schedule service from the car?",
    ];
  }

  return [
    "What does the tire pressure warning mean?",
    "How do I reset the oil service reminder?",
    "Where can I find maintenance schedules?",
  ];
};

const ALL_MANUALS_VALUE = "__all__";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [manuals, setManuals] = useState<Manual[]>([]);
  const [manualsLoading, setManualsLoading] = useState(true);
  const [manualError, setManualError] = useState<string | null>(null);
  const [selectedManualId, setSelectedManualId] = useState<string>(ALL_MANUALS_VALUE);
  const [suggestions, setSuggestions] = useState<string[]>(deriveSuggestions(null));

  const fetchManuals = useCallback(async () => {
    try {
      setManualsLoading(true);
      const response = await fetch(`${API_URL}/api/manuals`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Failed to fetch manuals (${response.status})`);
      }
      const data = (await response.json()) as ManualListResponse;
      setManuals(data.manuals);
      setManualError(null);
    } catch (error) {
      console.error(error);
      setManualError("Unable to load manuals.");
    } finally {
      setManualsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchManuals();
  }, [fetchManuals]);

  const readyManuals = useMemo(() => manuals.filter((manual) => manual.status === "ready"), [manuals]);

  useEffect(() => {
    const manual = readyManuals.find((item) => item.manual_id === selectedManualId);
    setSuggestions(deriveSuggestions(manual ?? null));
  }, [readyManuals, selectedManualId]);

  const currentManualLabel = useMemo(() => {
    if (selectedManualId === ALL_MANUALS_VALUE) {
      return "All Manuals";
    }
    const manual = manuals.find((item) => item.manual_id === selectedManualId);
    if (!manual) return selectedManualId;
    const modelYear = [manual.year, manual.model].filter(Boolean).join(" ");
    return [manual.brand ?? "Manual", modelYear].filter(Boolean).join(" • ") || manual.manual_id;
  }, [manuals, selectedManualId]);

  const handleSend = useCallback(async () => {
    if (!input.trim()) {
      return;
    }
    const question = input.trim();
    setInput("");
    const manualIdToSend = selectedManualId === ALL_MANUALS_VALUE ? undefined : selectedManualId;
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
        manualId: manualIdToSend ?? "All Manuals",
      },
    ]);
    setIsSending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          manual_id: manualIdToSend,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        const detail = typeof errorBody?.detail === "string" ? errorBody.detail : "Unexpected error";
        throw new Error(detail);
      }

      const data = (await response.json()) as { answer: string };
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer ?? "I wasn't able to find an answer in the uploaded manuals.",
          manualId: manualIdToSend ?? "All Manuals",
        },
      ]);
    } catch (error) {
      const description = error instanceof Error ? error.message : "Unable to contact the assistant.";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ ${description}`,
          manualId: manualIdToSend ?? "All Manuals",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }, [input, selectedManualId]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!isSending) {
        void handleSend();
      }
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-10">
      <section className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 shadow-xl shadow-slate-900/40">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">Chat with your Manuals</h1>
            <p className="text-sm text-slate-400">
              Ask questions and get concise answers sourced directly from your uploaded manuals.
            </p>
          </div>
          <button
            type="button"
            onClick={() => fetchManuals()}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-200 transition hover:bg-slate-800"
          >
            <RefreshCcw className="h-4 w-4" />
            Refresh manuals
          </button>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400">
              Manual selection
            </label>
            <select
              value={selectedManualId}
              onChange={(event) => setSelectedManualId(event.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none"
            >
              <option value={ALL_MANUALS_VALUE} className="bg-slate-900">
                All Manuals
              </option>
              {readyManuals.map((manual) => {
                const labelParts = [manual.brand, manual.model, manual.year].filter(Boolean);
                const label = labelParts.length > 0 ? labelParts.join(" • ") : manual.filename ?? manual.manual_id;
                return (
                  <option key={manual.manual_id} value={manual.manual_id} className="bg-slate-900">
                    {label}
                  </option>
                );
              })}
            </select>
            {manualsLoading && (
              <p className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                <Loader2 className="h-3 w-3 animate-spin" /> Loading manuals...
              </p>
            )}
            {manualError && (
              <p className="mt-2 flex items-center gap-2 text-xs text-amber-400">
                <AlertCircle className="h-3 w-3" /> {manualError}
              </p>
            )}
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300">
            <p className="text-xs uppercase tracking-wide text-slate-400">Current selection</p>
            <p className="mt-1 text-sm font-medium text-slate-100">{currentManualLabel}</p>
            <p className="mt-1 text-xs text-slate-500">
              Manuals update automatically after uploads finish processing.
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-lg shadow-slate-900/30">
        <h2 className="text-sm font-semibold text-slate-200">Suggested Questions</h2>
        <p className="text-xs text-slate-500">Based on the selected manual.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {suggestions.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setInput(item)}
              className="rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs text-slate-200 transition hover:border-sky-500 hover:text-sky-300"
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      <section className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/70 shadow-xl shadow-slate-900/40">
        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-slate-400">
              <p className="text-lg font-medium text-slate-200">Ready when you are</p>
              <p className="max-w-md text-sm text-slate-400">
                Ask about warning lights, maintenance reminders, or any topic covered in your manuals. You can switch
                manuals at any time.
              </p>
            </div>
          ) : (
            messages.map((message, index) => <MessageBubble key={index} message={message} />)
          )}
        </div>
        <div className="border-t border-slate-800 bg-slate-950/80 p-4">
          <div className="relative">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              rows={3}
              placeholder="Ask a question about your manual..."
              className="w-full resize-none rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none"
            />
            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={isSending || !input.trim()}
              className={clsx(
                "absolute bottom-3 right-3 inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
                isSending || !input.trim()
                  ? "cursor-not-allowed bg-slate-800/60 text-slate-500"
                  : "bg-sky-600 text-white hover:bg-sky-500"
              )}
            >
              {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              Send
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
