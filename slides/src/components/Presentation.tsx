"use client";

import { useState, useEffect, useCallback } from "react";
import { Slide } from "./PresentationSlideUI";

export default function Presentation({ slides }: { slides: Slide[] }) {
    const [current, setCurrent] = useState(0);
    const [showNotes, setShowNotes] = useState(false);
    const [direction, setDirection] = useState<"right" | "left">("right");
    const [animKey, setAnimKey] = useState(0);

    const goTo = useCallback(
        (n: number) => {
            if (n < 0 || n >= slides.length) return;
            setDirection(n > current ? "right" : "left");
            setCurrent(n);
            setAnimKey((k) => k + 1);
        },
        [current, slides.length]
    );

    const next = useCallback(() => goTo(current + 1), [current, goTo]);
    const prev = useCallback(() => goTo(current - 1), [current, goTo]);

    useEffect(() => {
        function onKey(e: KeyboardEvent) {
            if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); next(); }
            else if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
            else if (e.key === "n" || e.key === "N") setShowNotes((s) => !s);
            else if (e.key === "f" || e.key === "F") {
                if (!document.fullscreenElement) document.documentElement.requestFullscreen();
                else document.exitFullscreen();
            }
            else if (e.key === "Escape") setShowNotes(false);
        }
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [next, prev]);

    const slide = slides[current];
    const progress = slides.length > 0 ? ((current + 1) / slides.length) * 100 : 0;

    if (!slide) {
        return (
            <div className="flex h-screen items-center justify-center text-white bg-[#08080f]">
                No slides provided.
            </div>
        );
    }

    return (
        <div className="relative h-screen flex flex-col overflow-hidden select-none">
            {/* Background */}
            <div className="fixed inset-0 bg-[#08080f]" />
            <div className="fixed top-[-200px] left-[-100px] w-[600px] h-[600px] rounded-full bg-indigo-900/30 blur-[150px] animate-float" />
            <div
                className="fixed bottom-[-200px] right-[-100px] w-[600px] h-[600px] rounded-full bg-purple-900/25 blur-[150px] animate-float"
                style={{ animationDelay: "3s" }}
            />
            <div
                className="fixed top-[40%] right-[20%] w-[400px] h-[400px] rounded-full bg-fuchsia-900/15 blur-[120px] animate-float"
                style={{ animationDelay: "5s" }}
            />

            {/* Progress Bar */}
            <div className="relative z-20 h-1 bg-white/5">
                <div className="progress-bar h-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: `${progress}%` }} />
            </div>

            {/* Slide Content */}
            <div className="relative z-10 flex-1 flex items-center justify-center px-6 py-8">
                <div
                    key={animKey}
                    className={`w-full max-w-4xl ${direction === "right" ? "animate-slide-in-right" : "animate-slide-in-left"}`}
                >
                    {/* Tag + Title */}
                    <div className="mb-5">
                        {slide.tag && <span className={`badge ${slide.tagColor} mb-3 inline-block`}>{slide.tag}</span>}
                        {slide.title && (
                            <h2 className="text-3xl md:text-4xl font-bold text-white">{slide.title}</h2>
                        )}
                    </div>

                    {/* Content Card */}
                    <div className="glass rounded-2xl p-6 md:p-8 overflow-y-auto" style={{ maxHeight: showNotes ? "50vh" : "65vh" }}>
                        {slide.content}
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="relative z-20 flex items-center justify-between px-6 py-3">
                <div className="flex items-center gap-3">
                    <button
                        onClick={prev}
                        disabled={current === 0}
                        className="p-2 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M15 18l-6-6 6-6" />
                        </svg>
                    </button>
                    <span className="text-xs font-mono text-slate-600">
                        {String(current + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}
                    </span>
                    <button
                        onClick={next}
                        disabled={current === slides.length - 1}
                        className="p-2 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9 18l6-6-6-6" />
                        </svg>
                    </button>
                </div>

                {/* Slide dots */}
                <div className="hidden md:flex items-center gap-1">
                    {slides.map((_, i) => (
                        <button
                            key={i}
                            onClick={() => goTo(i)}
                            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${i === current ? "bg-indigo-400 w-4" : "bg-white/10 hover:bg-white/20"
                                }`}
                        />
                    ))}
                </div>

                {/* Controls */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowNotes((s) => !s)}
                        className={`p-2 rounded-lg text-xs transition-all ${showNotes ? "text-indigo-400 bg-indigo-400/10" : "text-slate-600 hover:text-slate-300 hover:bg-white/5"
                            }`}
                        title="Toggle speaker notes (N)"
                    >
                        Notes
                    </button>
                    <button
                        onClick={() => {
                            if (!document.fullscreenElement) document.documentElement.requestFullscreen();
                            else document.exitFullscreen();
                        }}
                        className="p-2 rounded-lg text-slate-600 hover:text-slate-300 hover:bg-white/5 transition-all"
                        title="Toggle fullscreen (F)"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
                        </svg>
                    </button>
                </div>
            </div>

            {/* Speaker Notes Panel */}
            {showNotes && (
                <div className="speaker-notes relative z-20 px-6 py-4 max-h-[25vh] overflow-y-auto">
                    <p className="text-[11px] text-slate-600 uppercase tracking-wider mb-2">Speaker Notes</p>
                    <p className="text-sm text-slate-400 leading-relaxed">{slide.notes}</p>
                </div>
            )}
        </div>
    );
}
