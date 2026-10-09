"use client";

import { useEffect, useState } from "react";

type Commitment = {
  id: string;
  person: string;
  task: string;
  deadline: string;
  status: "pending" | "completed" | "unclear";
  source: string;
};

type Clarification = {
  issue: string;
  source: string;
};

type AnalysisResult = {
  id: string;
  commitments: Commitment[];
  needs_clarification: Clarification[];
  model_used: string;
};

type SavedConversation = {
  id: string;
  content: string;
  model_used: string;
  created_at: string;
};

const SAMPLE_CONVERSATION = `Rahul: I'll make the PPT tonight.
Sujal: I'll ask sir about the submission deadline tomorrow morning.
Aman: Does anyone have the circuit diagram?
Priya: I'll finish the introduction section by Friday.
Rahul: Actually, I already completed the PPT.`;

export default function Home() {
  const [conversation, setConversation] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [savedConversations, setSavedConversations] = useState<SavedConversation[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [openingConversationId, setOpeningConversationId] = useState<string | null>(null);

  async function loadConversations() {
    try {
      const response = await fetch("/api/conversations");
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load conversations.");
      }

      setSavedConversations(data.conversations || []);
    } catch (err) {
      console.error("Failed to load conversation history:", err);
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  async function analyzeConversation() {
    if (!conversation.trim()) {
      setError("Please paste a group conversation first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed.");
      }

      setResult(data);
      await loadConversations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong while analyzing.");
    } finally {
      setLoading(false);
    }
  }

  async function openSavedConversation(item: SavedConversation) {
    setOpeningConversationId(item.id);
    setError("");

    try {
      const response = await fetch(`/api/conversations/${item.id}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to open saved conversation.");
      }

      setConversation(data.conversation.content);
      setResult({
        id: data.conversation.id,
        commitments: data.commitments || [],
        needs_clarification: data.clarifications || [],
        model_used: data.conversation.model_used || item.model_used,
      });
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to open saved conversation.");
    } finally {
      setOpeningConversationId(null);
    }
  }

  function loadSample() {
    setConversation(SAMPLE_CONVERSATION);
    setResult(null);
    setError("");
  }

  function clearAll() {
    setConversation("");
    setResult(null);
    setError("");
  }

  const pendingCount =
    result?.commitments.filter((item) => item.status === "pending").length ?? 0;
  const completedCount =
    result?.commitments.filter((item) => item.status === "completed").length ?? 0;
  const clarificationCount = result?.needs_clarification.length ?? 0;

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10 bg-slate-950/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 font-bold">
              CC
            </div>
            <div>
              <h1 className="text-xl font-bold">College Coordination Copilot</h1>
              <p className="text-xs text-slate-400">
                Turn messy group chats into clear commitments
              </p>
            </div>
          </div>
          <div className="hidden rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-300 sm:block">
            ● Gemma 4 connected
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-10">
        <section className="mb-8">
          <p className="mb-3 text-sm font-medium text-indigo-400">AI-POWERED COORDINATION</p>
          <h2 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
            Make your group chat<span className="text-indigo-400"> actionable.</span>
          </h2>
          <p className="mt-4 max-w-2xl text-lg text-slate-400">
            Paste your college group conversation and let Gemma identify who promised what,
            deadlines, completed work, and what still needs clarification.
          </p>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-2xl">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold">Group conversation</h3>
              <p className="text-sm text-slate-400">
                Paste messages exactly as they appear in your group chat.
              </p>
            </div>
            <button
              onClick={loadSample}
              className="rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10"
            >
              Load sample
            </button>
          </div>

          <textarea
            value={conversation}
            onChange={(event) => setConversation(event.target.value)}
            placeholder={`Rahul: I'll make the PPT tonight.\nSujal: I'll ask sir about the deadline tomorrow.\nAman: Does anyone have the circuit diagram?`}
            className="min-h-[260px] w-full resize-y rounded-xl border border-white/10 bg-slate-900 p-4 text-sm leading-7 text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-500"
          />

          {error && (
            <div className="mt-4 rounded-lg border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="mt-4 flex flex-wrap justify-end gap-3">
            <button
              onClick={clearAll}
              disabled={loading || !conversation}
              className="rounded-xl border border-white/10 px-5 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Clear
            </button>
            <button
              onClick={analyzeConversation}
              disabled={loading}
              className="rounded-xl bg-indigo-500 px-6 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-wait disabled:opacity-60"
            >
              {loading ? "Analyzing with Gemma..." : "Analyze Conversation →"}
            </button>
          </div>
        </section>

        <section className="mt-10 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h3 className="text-xl font-semibold">Saved conversation history</h3>
              <p className="mt-1 text-sm text-slate-400">
                Select a saved conversation to reopen its commitments and statuses.
              </p>
            </div>
            <button
              onClick={() => {
                setHistoryLoading(true);
                void loadConversations();
              }}
              className="rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/10"
            >
              Refresh history
            </button>
          </div>

          {historyLoading ? (
            <p className="text-sm text-slate-400">Loading saved conversations...</p>
          ) : savedConversations.length === 0 ? (
            <p className="text-sm text-slate-400">No saved conversations found yet.</p>
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {savedConversations.map((item) => (
                <button
                  key={item.id}
                  onClick={() => void openSavedConversation(item)}
                  disabled={openingConversationId !== null}
                  className="rounded-xl border border-white/10 bg-slate-900/70 p-4 text-left transition hover:border-indigo-400/50 hover:bg-slate-900 disabled:opacity-60"
                >
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <span className="text-xs text-slate-500">
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                    <span className="text-xs text-indigo-300">
                      {openingConversationId === item.id ? "Opening..." : "Open →"}
                    </span>
                  </div>
                  <p className="line-clamp-3 whitespace-pre-wrap text-sm text-slate-200">
                    {item.content}
                  </p>
                </button>
              ))}
            </div>
          )}
        </section>

        {result && (
          <section className="mt-10">
            <div className="mb-6 grid gap-4 sm:grid-cols-3">
              <StatCard label="Pending" value={pendingCount} description="Tasks still to be done" />
              <StatCard label="Completed" value={completedCount} description="Tasks marked complete" />
              <StatCard
                label="Needs clarification"
                value={clarificationCount}
                description="Questions or ambiguity"
              />
            </div>

            <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold">Commitments</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    What your team members have committed to doing.
                  </p>
                </div>
                {result.commitments.length === 0 ? (
                  <EmptyState message="No clear commitments were found." />
                ) : (
                  <div className="space-y-4">
                    {result.commitments.map((item, index) => (
                      <CommitmentCard
                        key={item.id || `${item.person}-${item.task}-${index}`}
                        item={item}
                        onStatusUpdated={(id, status) => {
                          setResult((current) =>
                            current
                              ? {
                                  ...current,
                                  commitments: current.commitments.map((commitment) =>
                                    commitment.id === id ? { ...commitment, status } : commitment
                                  ),
                                }
                              : current
                          );
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.04] p-6">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold">Needs clarification</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    Things your team should resolve.
                  </p>
                </div>
                {result.needs_clarification.length === 0 ? (
                  <EmptyState message="No clarification items found." />
                ) : (
                  <div className="space-y-4">
                    {result.needs_clarification.map((item, index) => (
                      <div
                        key={`${item.issue}-${index}`}
                        className="rounded-xl border border-amber-400/20 bg-slate-950/50 p-4"
                      >
                        <div className="mb-2 flex items-start gap-3">
                          <span className="mt-1 text-amber-400">!</span>
                          <p className="font-medium text-white">{item.issue}</p>
                        </div>
                        <p className="ml-6 text-sm italic text-slate-400">“{item.source}”</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <p className="mt-5 text-right text-xs text-slate-500">
              Analyzed with {result.model_used}
            </p>
          </section>
        )}
      </div>
    </main>
  );
}

function StatCard({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{description}</p>
    </div>
  );
}

function CommitmentCard({
  item,
  onStatusUpdated,
}: {
  item: Commitment;
  onStatusUpdated: (id: string, status: Commitment["status"]) => void;
}) {
  const [status, setStatus] = useState(item.status);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    setStatus(item.status);
  }, [item.id, item.status]);

  const statusStyles = {
    pending: "border-blue-400/20 bg-blue-400/10 text-blue-300",
    completed: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    unclear: "border-amber-400/20 bg-amber-400/10 text-amber-300",
  };

  async function updateStatus(newStatus: Commitment["status"]) {
    if (!item.id) {
      alert("This commitment has no database ID. Please analyze the conversation again.");
      return;
    }

    setUpdating(true);
    try {
      const response = await fetch("/api/commitments", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id, status: newStatus }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to update status.");
      }

      setStatus(newStatus);
      onStatusUpdated(item.id, newStatus);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Could not update the commitment status.");
    } finally {
      setUpdating(false);
    }
  }

  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/70 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-lg font-semibold">{item.person}</p>
          <p className="mt-1 text-slate-300">{item.task}</p>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-medium capitalize ${statusStyles[status]}`}>
          {status}
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-3 text-sm">
        <span className="rounded-lg bg-white/5 px-3 py-2 text-slate-300">
          Deadline: <strong>{item.deadline || "Not specified"}</strong>
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => void updateStatus("pending")}
          disabled={updating}
          className="rounded-lg border border-blue-400/20 bg-blue-400/10 px-3 py-2 text-xs font-medium text-blue-300 transition hover:bg-blue-400/20 disabled:opacity-50"
        >
          Mark Pending
        </button>
        <button
          onClick={() => void updateStatus("completed")}
          disabled={updating}
          className="rounded-lg border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-medium text-emerald-300 transition hover:bg-emerald-400/20 disabled:opacity-50"
        >
          Mark Completed
        </button>
        <button
          onClick={() => void updateStatus("unclear")}
          disabled={updating}
          className="rounded-lg border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-medium text-amber-300 transition hover:bg-amber-400/20 disabled:opacity-50"
        >
          Mark Unclear
        </button>
      </div>
      <div className="mt-4 border-t border-white/5 pt-3">
        <p className="text-xs text-slate-500">Source</p>
        <p className="mt-1 text-sm italic text-slate-400">“{item.source}”</p>
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-dashed border-white/10 p-8 text-center">
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  );
}
