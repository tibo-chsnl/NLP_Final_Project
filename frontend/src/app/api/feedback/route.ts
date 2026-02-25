import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
  const { context, question, answer, original_answer, positive } = await req.json();

  if (!supabase) {
    return NextResponse.json({ success: true, stored: false });
  }

  const { error } = await supabase.from("feedback").insert({
    context,
    question,
    answer,
    original_answer,
    positive,
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
