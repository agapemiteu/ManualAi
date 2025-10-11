import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call HuggingFace Space API
    const HF_SPACE_URL = 'https://agapemiteu-manualai.hf.space/api/predict';
    
    const response = await fetch(HF_SPACE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data: [message]
      }),
    });

    if (!response.ok) {
      throw new Error(`HuggingFace API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Extract the answer from HF response
    // HF Gradio API returns: { data: [answer, chunks, confidence, latency] }
    const [answer, chunks, confidence, latency] = data.data;

    return NextResponse.json({
      answer,
      chunks,
      confidence,
      latency,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get response',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// Optional: Add rate limiting in production
export const runtime = 'edge'; // Use Edge runtime for better performance
