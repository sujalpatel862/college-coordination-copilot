import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

type RouteContext = {
params: Promise<{ id: string }>;
};

export async function GET(
request: Request,
{ params }: RouteContext
) {
try {
const { id } = await params;
const supabase = await createClient();

// Load the selected conversation
const { data: conversation, error: conversationError } =
  await supabase
    .from("conversations")
    .select("id, content, model_used, created_at")
    .eq("id", id)
    .single();

if (conversationError || !conversation) {
  console.error("Load conversation error:", conversationError);

  return NextResponse.json(
    { error: "Conversation not found." },
    { status: 404 }
  );
}

// Load commitments belonging to this conversation
const { data: commitments, error: commitmentsError } =
  await supabase
    .from("commitments")
    .select("id, person, task, deadline, status, source")
    .eq("conversation_id", id);

if (commitmentsError) {
  console.error("Load commitments error:", commitmentsError);

  return NextResponse.json(
    { error: "Failed to load commitments." },
    { status: 500 }
  );
}

// Load clarification issues belonging to this conversation
const { data: clarifications, error: clarificationsError } =
  await supabase
    .from("clarifications")
    .select("issue, source")
    .eq("conversation_id", id);

if (clarificationsError) {
  console.error("Load clarifications error:", clarificationsError);

  return NextResponse.json(
    { error: "Failed to load clarifications." },
    { status: 500 }
  );
}

return NextResponse.json({
  conversation,
  commitments: commitments ?? [],
  clarifications: clarifications ?? [],
});

} catch (error) {
console.error("Conversation API error:", error);

return NextResponse.json(
  { error: "An unexpected error occurred while loading the conversation." },
  { status: 500 }
);


}
}
