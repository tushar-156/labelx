import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    const body = await req.json();

    const backendRes = await fetch(`${backendUrl}/routine-layering`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Connection": "close"
      },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(5000)
    });

    if (!backendRes.ok) {
      return NextResponse.json({ ok: false, error: `Backend responded with ${backendRes.status}` }, { status: backendRes.status });
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ ok: false, error: err.message || "Failed to reach routine layering engine" }, { status: 500 });
  }
}
