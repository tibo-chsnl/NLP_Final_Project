import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { context, question } = await req.json();

    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

    const res = await fetch(`${backendUrl}/api/v1/qa/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context, question }),
    });

    if (!res.ok) {
        const errText = await res.text();
        console.error("Backend error:", res.status, errText);
        return NextResponse.json({
            text: `(Erreur du backend: ${res.status}) - ${errText}`,
            start: 0,
            end: 0,
            confidence: 0,
        });
    }

    const data = await res.json();
    const answerText = data.answer || "";
    
    // Case-insensitive search for answer index
    const lowerContext = context.toLowerCase();
    const lowerAnswer = answerText.toLowerCase();
    const start = lowerContext.indexOf(lowerAnswer);
    
    return NextResponse.json({
      text: answerText,
      start: start >= 0 ? start : 0,
      end: start >= 0 ? start + answerText.length : 0,
      confidence: data.confidence || 0,
    });
  } catch (err: any) {
    console.error("Fetch error:", err);
    return NextResponse.json({
        text: `(Erreur de connexion): ${err.message}`,
        start: 0,
        end: 0,
        confidence: 0,
    });
  }
}
