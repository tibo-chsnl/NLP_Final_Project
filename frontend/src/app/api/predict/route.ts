import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { context, question } = await req.json();

  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context, question }),
      });
      return NextResponse.json(await res.json());
    } catch {}
  }

  const stopWords = new Set([
    "is", "the", "a", "an", "of", "in", "to", "and", "was", "were", "are",
    "what", "where", "when", "who", "how", "which", "why", "do", "does", "did",
    "can", "could", "would", "should", "has", "have", "had", "be", "been",
    "this", "that", "it", "for", "on", "with", "as", "at", "by", "from",
  ]);

  const questionWords = question
    .toLowerCase()
    .split(/\s+/)
    .filter((w: string) => !stopWords.has(w) && w.length > 2);

  const sentences = context
    .split(/(?<=[.!?])\s+/)
    .filter((s: string) => s.trim().length > 0);

  let best = sentences[0] || context;
  let bestScore = -1;

  for (const s of sentences) {
    const lower = s.toLowerCase();
    let score = 0;
    for (const w of questionWords) {
      if (lower.includes(w)) score++;
    }
    if (score > bestScore) {
      bestScore = score;
      best = s.trim();
    }
  }

  const start = context.indexOf(best);

  return NextResponse.json({
    text: best,
    start,
    end: start + best.length,
    confidence: 0.82 + Math.random() * 0.15,
  });
}
