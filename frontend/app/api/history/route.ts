import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    const { searchParams } = new URL(req.url);
    const userId = searchParams.get("user_id");
    
    const targetUrl = userId ? `${backendUrl}/history?user_id=${userId}` : `${backendUrl}/history`;
    
    const backendRes = await fetch(targetUrl, {
      method: "GET",
      headers: { 
        "Content-Type": "application/json",
        "Connection": "close"
      },
      cache: "no-store",
      signal: AbortSignal.timeout(2500)
    });

    if (!backendRes.ok) {
      return NextResponse.json([]);
    }

    const data = await backendRes.json();
    return NextResponse.json(Array.isArray(data) ? data : []);
  } catch {
    // Non-blocking fallback: return empty history so the page loads instantly without stalling
    return NextResponse.json([]);
  }
}
