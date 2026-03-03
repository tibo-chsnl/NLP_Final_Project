"use client";

import { useState } from "react";

export default function Home() {
  const [context, setContext] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<{
    text: string;
    start: number;
    end: number;
    confidence: number;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [showCorrection, setShowCorrection] = useState(false);
  const [correction, setCorrection] = useState("");

  async function handleAsk() {
    if (!context.trim() || !question.trim()) return;
    setLoading(true);
    setAnswer(null);
    setFeedbackSent(false);
    setFeedbackError(null);
    setShowCorrection(false);
    setCorrection("");
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context, question }),
      });
      const data = await res.json();
      setAnswer(data);
    } catch {
      setAnswer(null);
    } finally {
      setLoading(false);
    }
  }

  async function sendFeedback(positive: boolean) {
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          context,
          question,
          answer: positive ? answer?.text : correction,
          original_answer: answer?.text,
          positive,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        if (res.status === 503) {
          setFeedbackError("Feedback service unavailable");
        } else {
          setFeedbackError(data.error || "Failed to send feedback");
        }
        return;
      }

      setFeedbackSent(true);
      setShowCorrection(false);
    } catch {
      setFeedbackError("Network error — could not send feedback");
    }
  }

  function renderHighlighted() {
    if (!answer) return context;
    const { start, end } = answer;
    if (start < 0 || end < 0) return context;
    return (
      <>
        {context.slice(0, start)}
        <span className="highlight-answer">{context.slice(start, end)}</span>
        {context.slice(end)}
      </>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="fixed inset-0 bg-[#08080f]" />
      <div
        className="fixed top-[-200px] left-[-100px] w-[600px] h-[600px] rounded-full bg-indigo-900/30 blur-[150px] animate-float"
      />
      <div
        className="fixed bottom-[-200px] right-[-100px] w-[600px] h-[600px] rounded-full bg-purple-900/25 blur-[150px] animate-float"
        style={{ animationDelay: "3s" }}
      />
      <div
        className="fixed top-[40%] right-[20%] w-[400px] h-[400px] rounded-full bg-fuchsia-900/15 blur-[120px] animate-float"
        style={{ animationDelay: "5s" }}
      />

      <div className="relative z-10 min-h-screen flex flex-col items-center px-4 py-16">
        <div className="text-center mb-12 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/20 bg-indigo-500/5 text-indigo-300 text-xs mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            NLP-Powered Question Answering
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
              Document QA
            </span>
            <br />
            <span className="text-white/90">Assistant</span>
          </h1>
          <p className="text-slate-500 text-lg max-w-md mx-auto">
            Paste any document, ask a question, and get an instant answer powered by deep learning.
          </p>
        </div>

        <div className="w-full max-w-2xl animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
          <div className="glass rounded-2xl p-6 md:p-8">
            <div className="mb-5">
              <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">
                Context
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Paste your paragraph or document here..."
                rows={5}
                className="w-full rounded-xl px-4 py-3 text-sm bg-white/[0.03] border border-white/[0.06] text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 resize-none transition-all"
              />
            </div>

            <div className="mb-6">
              <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">
                Question
              </label>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                placeholder="What would you like to know?"
                className="w-full rounded-xl px-4 py-3 text-sm bg-white/[0.03] border border-white/[0.06] text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 transition-all"
              />
            </div>

            <button
              onClick={handleAsk}
              disabled={loading || !context.trim() || !question.trim()}
              className="w-full py-3 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-[0_8px_30px_rgba(99,102,241,0.3)] active:scale-[0.98]"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                "Get Answer"
              )}
            </button>
          </div>

          {answer && (
            <div className="mt-6 animate-fade-in-up">
              <div className="glass rounded-2xl p-6 md:p-8">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-medium text-emerald-400 uppercase tracking-wider">
                    Answer
                  </span>
                  {answer.confidence != null && (
                    <span className="ml-auto text-[11px] text-slate-600 font-mono">
                      {(answer.confidence * 100).toFixed(1)}% confidence
                    </span>
                  )}
                </div>

                <p className="text-2xl font-semibold text-white leading-snug mb-6">
                  {answer.text}
                </p>

                <div className="pt-4 border-t border-white/5">
                  <p className="text-[11px] text-slate-600 uppercase tracking-wider mb-2">Source</p>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    {renderHighlighted()}
                  </p>
                </div>
              </div>

              {!feedbackSent ? (
                <div className="mt-4 flex items-center gap-2">
                  <span className="text-xs text-slate-600">Was this helpful?</span>
                  <button
                    onClick={() => sendFeedback(true)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-emerald-400 hover:bg-emerald-400/10 transition-all"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M7 10v12" />
                      <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setShowCorrection(true)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17 14V2" />
                      <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88z" />
                    </svg>
                  </button>
                </div>
              ) : (
                <p className="mt-4 text-xs text-indigo-400">Thanks for your feedback!</p>
              )}

              {feedbackError && (
                <p className="mt-4 text-xs text-red-400">{feedbackError}</p>
              )}

              {showCorrection && !feedbackSent && (
                <div className="mt-3 flex gap-2">
                  <input
                    type="text"
                    value={correction}
                    onChange={(e) => setCorrection(e.target.value)}
                    placeholder="What should the correct answer be?"
                    className="flex-1 rounded-xl px-4 py-2.5 text-sm bg-white/[0.03] border border-white/[0.06] text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/40 transition-all"
                    onKeyDown={(e) => e.key === "Enter" && correction.trim() && sendFeedback(false)}
                  />
                  <button
                    onClick={() => sendFeedback(false)}
                    disabled={!correction.trim()}
                    className="px-5 py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 disabled:opacity-40 transition-all"
                  >
                    Send
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <p className="mt-12 text-[11px] text-slate-700">
          Document QA Assistant — NLP & MLOps Project
        </p>
      </div>
    </div>
  );
}
