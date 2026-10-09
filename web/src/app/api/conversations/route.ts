import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("conversations")
      .select("id, content, model_used, created_at")
      .order("created_at", { ascending: false })
      .limit(20);

    if (error) {
      console.error("Load conversations error:", error);

      return NextResponse.json(
        { error: "Failed to load conversations." },
        { status: 500 }
      );
    }

    return NextResponse.json({ conversations: data ?? [] });
  } catch (error) {
    console.error("Conversations API error:", error);

    return NextResponse.json(
      { error: "Failed to load conversations." },
      { status: 500 }
    );
  }
}

