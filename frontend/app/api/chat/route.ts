import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    
    // Forward the request to the new FastAPI backend
    const backendRes = await fetch(`${backendUrl}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!backendRes.ok) {
      const errorText = await backendRes.text();
      throw new Error(`Backend returned ${backendRes.status}: ${errorText}`);
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
    
  } catch (err: any) {
    let message = err instanceof Error ? err.message : "chat turn failed";
    if (message.includes("fetch failed") || err?.cause?.code === "ECONNREFUSED" || err?.code === "ECONNREFUSED") {
      message = "Backend server is not running on http://127.0.0.1:8000. Please start uvicorn in your backend terminal.";
    }
    console.error("API Proxy Error:", message);
    return NextResponse.json({ ok: false, error: message }, { status: 503 });
  }
}
