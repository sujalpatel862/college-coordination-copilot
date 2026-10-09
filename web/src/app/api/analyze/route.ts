import { NextResponse } from "next/server";
import { GoogleGenAI } from "@google/genai";
import { createClient } from "@/lib/supabase/server";

const MODEL_NAME =
  process.env.GEMINI_MODEL || "gemma-4-26b-a4b-it";

const SYSTEM_PROMPT = `You are College Coordination Copilot, an assistant that analyzes college group-chat conversations and extracts structured commitments.

STRICT RULES:
1. NEVER invent a person. Only use names that appear in the conversation.
2. NEVER invent a task. Only extract tasks that were explicitly stated.
3. NEVER invent a deadline. If no deadline is stated, use "unclear".
4. NEVER invent a status. Use "pending", "completed", or "unclear".
5. If information is missing, use "unclear".
6. Questions are NOT commitments. Put them under needs_clarification.
7. Preserve the exact original source message for every item.
8. If a person changes their commitment, prefer their LATEST clear commitment.
9. Identify unresolved questions under needs_clarification.
10. Identify ambiguous responsibilities under needs_clarification.
11. Identify conflicting commitments under needs_clarification.
12. Conditional commitments should go under needs_clarification unless the condition is clearly met.
13. Return ONLY valid JSON.

OUTPUT FORMAT:
{
  "commitments": [
    {
      "person": "name",
      "task": "task description",
      "deadline": "deadline or unclear",
      "status": "pending, completed, or unclear",
      "source": "exact source message"
    }
  ],
  "needs_clarification": [
    {
      "issue": "what needs clarification",
      "source": "exact source message"
    }
  ]
}`;

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const conversation = String(body.conversation || "").trim();

    if (!conversation) {
      return NextResponse.json(
        { error: "Please provide a conversation to analyze." },
        { status: 400 }
      );
    }

    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        { error: "Gemini API key is not configured." },
        { status: 500 }
      );
    }

    // 1. Analyze with Gemma
    const ai = new GoogleGenAI({
      apiKey,
    });

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: `${SYSTEM_PROMPT}\n\nConversation:\n${conversation}`,
      config: {
        responseMimeType: "application/json",
        temperature: 0.1,
      },
    });

    if (!response.text) {
      return NextResponse.json(
        { error: "The model returned an empty response." },
        { status: 500 }
      );
    }

    let result;

    try {
      result = JSON.parse(response.text);
    } catch {
      return NextResponse.json(
        { error: "The model returned invalid JSON." },
        { status: 500 }
      );
    }

    // 2. Connect to Supabase
    const supabase = await createClient();

    // 3. Save the original conversation
    const { data: conversationRow, error: conversationError } =
      await supabase
        .from("conversations")
        .insert({
          content: conversation,
          model_used: MODEL_NAME,
        })
        .select("id, content, model_used, created_at")
        .single();

    if (conversationError) {
      console.error("Conversation save error:", conversationError);

      return NextResponse.json(
        { error: "Analysis succeeded, but saving the conversation failed." },
        { status: 500 }
      );
    }

    const conversationId = conversationRow.id;

    // 4. Save commitments
    const commitments = Array.isArray(result.commitments)
      ? result.commitments
      : [];

    if (commitments.length > 0) {
  const commitmentRows = commitments.map((item: {
    person?: string;
    task?: string;
    deadline?: string;
    status?: string;
    source?: string;
  }) => ({
    conversation_id: conversationId,
    person: item.person || "unclear",
    task: item.task || "unclear",
    deadline: item.deadline || "unclear",
    status: ["pending", "completed", "unclear"].includes(
      item.status || ""
    )
      ? item.status
      : "unclear",
    source: item.source || "",
  }));

  const { data: savedCommitments, error: commitmentsError } =
    await supabase
      .from("commitments")
      .insert(commitmentRows)
      .select(
        "id, conversation_id, person, task, deadline, status, source"
      );

  if (commitmentsError) {
    console.error("Commitments save error:", commitmentsError);

    return NextResponse.json(
      {
        error:
          "Conversation was saved, but commitments could not be saved.",
      },
      { status: 500 }
    );
  }

  // Replace the AI-only commitments with the database records.
  result.commitments = savedCommitments || [];
}
    // 5. Save clarification items
    const clarifications = Array.isArray(result.needs_clarification)
      ? result.needs_clarification
      : [];

    if (clarifications.length > 0) {
      const clarificationRows = clarifications.map((item: {
        issue?: string;
        source?: string;
      }) => ({
        conversation_id: conversationId,
        issue: item.issue || "unclear",
        source: item.source || "",
      }));

      const { error: clarificationError } = await supabase
        .from("clarifications")
        .insert(clarificationRows);

      if (clarificationError) {
        console.error(
          "Clarifications save error:",
          clarificationError
        );

        return NextResponse.json(
          {
            error:
              "Conversation was saved, but clarification items could not be saved.",
          },
          { status: 500 }
        );
      }
    }

    // 6. Return everything to the frontend
    return NextResponse.json({
      id: conversationId,
      conversation: conversationRow,
      commitments: result.commitments,
      needs_clarification: clarifications,
      model_used: MODEL_NAME,
    });
  } catch (error) {
    console.error("Gemini analysis error:", error);

    return NextResponse.json(
      { error: "Failed to analyze the conversation." },
      { status: 500 }
    );
  }
}
