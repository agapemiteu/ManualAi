import { NextRequest, NextResponse } from 'next/server';

// Use HuggingFace FastAPI backend (production)
// Or custom backend for development
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://agapemiteu-manualai.hf.space';

export async function POST(req: NextRequest) {
  try {
    const { message, manual_id } = await req.json();
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: message,  // FastAPI expects 'question' field
        manual_id: manual_id || null,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend API error: ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

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
