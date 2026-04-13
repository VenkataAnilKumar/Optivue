import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { prompt?: string; session_id?: string };
    const authHeader = req.headers.get('authorization') ?? '';

    if (!body.prompt) {
      return NextResponse.json({ error: 'prompt is required' }, { status: 400 });
    }

    // Proxy to FastAPI backend /cost/query (or a dedicated /agent endpoint)
    const backendRes = await fetch(`${API_BASE}/cost/query`, {
      method: 'GET',
      headers: { Authorization: authHeader },
    });

    if (!backendRes.ok) {
      return NextResponse.json(
        { response: 'I could not fetch data right now. Please try again.' },
        { status: 200 },
      );
    }

    const data = await backendRes.json();
    return NextResponse.json({
      response: `Based on the latest data: your total spend is $${(data.total_cost ?? 0).toLocaleString()}. Top driver: ${data.top_drivers?.[0]?.service ?? 'unknown'}.`,
      data_freshness_timestamp: data.data_freshness_timestamp,
    });
  } catch {
    return NextResponse.json(
      { response: 'An error occurred. Please try again.' },
      { status: 200 },
    );
  }
}
