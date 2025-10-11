import { NextResponse } from 'next/server';

// Query FastAPI backend for available manuals
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://agapemiteu-manualai.hf.space';

export async function GET() {
  try {
    // Fetch from FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/manuals`, {
      cache: 'no-store'
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Manuals API error:', error);
    // Return default manual even on error (graceful degradation)
    return NextResponse.json({
      manuals: [
        {
          manual_id: 'toyota-4runner-2023',
          status: 'ready',
          filename: '2023-Toyota-4runner-Manual.pdf',
          brand: 'Toyota',
          model: '4Runner',
          year: '2023',
          pages: 608,
        }
      ]
    });
  }
}

export const runtime = 'edge';
