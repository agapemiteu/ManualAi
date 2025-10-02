"use client";

import clsx from "clsx";
import { MessageCircle, User } from "lucide-react";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  manualId?: string | null;
};

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isAssistant = message.role === "assistant";
  return (
    <div
      className={clsx("flex gap-3", {
        "flex-row-reverse": !isAssistant,
      })}
    >
      <div
        className={clsx(
          "mt-1 flex h-8 w-8 items-center justify-center rounded-full",
          isAssistant ? "bg-sky-600/30 text-sky-300" : "bg-slate-700/40 text-slate-200"
        )}
      >
        {isAssistant ? <MessageCircle className="h-4 w-4" /> : <User className="h-4 w-4" />}
      </div>
      <div
        className={clsx(
          "max-w-full whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-md",
          isAssistant
            ? "bg-slate-800/60 text-slate-100 shadow-slate-900/40"
            : "bg-sky-600/70 text-white shadow-sky-900/40"
        )}
      >
        {message.manualId && (
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">
            Manual: {message.manualId}
          </p>
        )}
        <p>{message.content}</p>
      </div>
    </div>
  );
}
