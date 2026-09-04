import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    
    // Forward the multipart image formData to the FastAPI backend
    const backendRes = await fetch(`${backendUrl}/extract-label`, {
      method: "POST",
      body: formData,
    });

    if (!backendRes.ok) {
      const errorText = await backendRes.text();
      console.error(`Backend /extract-label returned ${backendRes.status}:`, errorText);
      return NextResponse.json(
        { ok: false, error: `Backend returned ${backendRes.status}: ${errorText}` },
        { status: backendRes.status }
      );
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (err: any) {
    let message = err instanceof Error ? err.message : "OCR label extraction failed";
    if (message.includes("fetch failed") || err?.cause?.code === "ECONNREFUSED" || err?.code === "ECONNREFUSED") {
      message = "Backend server is not running on http://127.0.0.1:8000. Please start uvicorn in your backend terminal.";
    }
    console.error("OCR Proxy Error:", message);
    return NextResponse.json({ ok: false, error: message }, { status: 503 });
  }
}
