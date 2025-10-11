import { NextRequest, NextResponse } from 'next/server';

// Use HuggingFace Space as backend (production)
// Or local backend for development
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://agapemiteu-manualai.hf.space';
const USE_HF_GRADIO = !process.env.NEXT_PUBLIC_API_URL; // Use Gradio API if no custom backend

export async function POST(req: NextRequest) {
  try {
    const { message, manual_id } = await req.json();
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    if (USE_HF_GRADIO) {
      // Call HuggingFace Gradio API
      const response = await fetch(`${BACKEND_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: [message] // Gradio expects data array
        }),
      });

      if (!response.ok) {
        throw new Error(`HuggingFace API error: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Extract from Gradio response: { data: [answer, chunks, confidence, latency] }
      const [answer, chunks, confidence, latency] = data.data;

      return NextResponse.json({
        response: answer,
        page_number: null, // Gradio returns formatted text, not structured data
        retrieved_chunks: chunks ? JSON.parse(chunks) : [],
        confidence: parseFloat(confidence) || 0.0,
        latency: parseFloat(latency) || 0.0,
        timestamp: new Date().toISOString(),
      });

    } else {
      // Call FastAPI backend (local development or custom deployment)
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          manual_id: manual_id || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.statusText}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
    }

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get response',
        details: error instanceof Error ? error.message : 'Unknown error',
        response: 'Sorry, I encountered an error processing your request. Please try again.'
      },
      { status: 500 }
    );
  }
}

export const runtime = 'edge';
