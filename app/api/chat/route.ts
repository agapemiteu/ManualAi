import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const question: unknown = body?.question;
    const manualId: unknown = body?.manual_id;

    if (typeof question !== "string" || question.trim().length === 0) {
      return NextResponse.json({ detail: "Question must be provided." }, { status: 400 });
    }

    const payload: Record<string, unknown> = { question: question.trim() };
    if (typeof manualId === "string" && manualId.trim().length > 0) {
      payload.manual_id = manualId.trim();
    }

    const response = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail = typeof data?.detail === "string" ? data.detail : "Chat service error.";
      return NextResponse.json({ detail }, { status: response.status });
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error("Chat route error", error);
    return NextResponse.json({ detail: "Unable to reach chat service." }, { status: 500 });
  }
}
