import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

const VALID_STATUSES = ["pending", "completed", "unclear"];

export async function PATCH(request: Request) {
  try {
    const body = await request.json();

    const id = String(body.id || "").trim();
    const status = String(body.status || "").trim();

    if (!id || !VALID_STATUSES.includes(status)) {
      return NextResponse.json(
        { error: "Invalid commitment ID or status." },
        { status: 400 }
      );
    }

    const supabase = await createClient();

    const { data, error } = await supabase
      .from("commitments")
      .update({ status })
      .eq("id", id)
      .select("id, conversation_id, person, task, deadline, status, source")
      .single();

    if (error) {
      console.error("Commitment update error:", error);

      return NextResponse.json(
        { error: "Failed to update commitment." },
        { status: 500 }
      );
    }

    return NextResponse.json({ commitment: data });
  } catch (error) {
    console.error("Commitment API error:", error);

    return NextResponse.json(
      { error: "Failed to update commitment." },
      { status: 500 }
    );
  }
}
