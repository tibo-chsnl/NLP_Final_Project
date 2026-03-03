"use client";

import Presentation from "../../components/Presentation";
import {
    Slide,
    DiagramFlow,
    DiagramFlowVertical,
    Table,
    Bullet,
    SectionLabel,
} from "../../components/PresentationSlideUI";

function buildSlides(): Slide[] {
    return [
        /* ── 1. Title ── */
        {
            tag: "MLOps Final Project",
            tagColor: "badge-emerald",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-4">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3">
                        <span className="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">
                            QA Model Deployment & Tracking
                        </span>
                    </h1>
                    <h2 className="text-xl md:text-2xl text-white/80 font-light mb-6">
                        MLOps Pipeline deep dive
                    </h2>
                    <div className="flex gap-2 flex-wrap justify-center mb-6">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                    <p className="text-slate-600 text-xs">
                        MLOps — M2 EFREI — March 2026
                    </p>
                </div>
            ),
            notes: "Good morning. Today we'll present our MLOps strategy for tracking, evaluating, and deploying our BiDAF QA model.",
        },

        /* ── 2. Agenda ── */
        {
            tag: "Overview",
            tagColor: "badge-emerald",
            title: "Agenda",
            content: (
                <div className="space-y-2 py-2">
                    {[
                        { n: "01", label: "MLOps Architecture Overview" },
                        { n: "02", label: "Experiment Tracking with MLflow" },
                        { n: "03", label: "Model Registry & Promotion" },
                        { n: "04", label: "Data & Model Versioning with DVC" },
                        { n: "05", label: "CI/CD Pipeline Operations" },
                        { n: "06", label: "Continuous Evaluation" },
                        { n: "07", label: "Live Demonstration" },
                        { n: "08", label: "Future Next Steps" },
                    ].map((item) => (
                        <div key={item.n} className="flex items-center gap-3 py-1 group">
                            <span className="text-xs font-mono text-emerald-500/60 w-6">{item.n}</span>
                            <span className="text-sm text-slate-300 group-hover:text-white transition-colors">{item.label}</span>
                        </div>
                    ))}
                </div>
            ),
            notes: "Our presentation will follow this structure. We'll start with the high-level architecture, move into tracking and versioning, and then cover our CI/CD setup.",
        },

        /* ── 3. High-Level Architecture ── */
        {
            tag: "Architecture",
            tagColor: "badge-teal",
            title: "MLOps Pipeline",
            content: (
                <div>
                    <DiagramFlowVertical items={[
                        { label: "🧑‍💻 Code & Logic", sub: "GitHub (CI/CD workflows)" },
                        { label: "📊 Tracking & Registry", sub: "MLflow (DAGsHub)" },
                        { label: "💾 Artifact Storage", sub: "DVC (Data & Checkpoints on DAGsHub)" },
                        { label: "☁️ Production Deployment", sub: "Render (FastAPI + Next.js)" }
                    ]} />
                    
                    <div className="flex gap-2 mt-4 justify-center">
                        <span className="badge badge-cyan">Fully Automated</span>
                        <span className="badge badge-indigo">Robust Scaling</span>
                    </div>
                </div>
            ),
            notes: "Our pipeline consists of code mapped via GitHub, artifacts tracked via DVC to DAGsHub, experiments recorded via MLflow on DAGsHub, and finally deployment occurring through Render for both backend and frontend.",
        },
        
        /* ── Final Wrap Up ── */
        {
            tag: "",
            tagColor: "",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-8">
                    <h1 className="text-5xl font-bold mb-4">
                        <span className="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">
                            Thank You
                        </span>
                    </h1>
                    <p className="text-lg text-slate-400 mb-6">Questions on our MLOps implementation?</p>
                    <div className="flex gap-3">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                </div>
            ),
            notes: "Thank you for your attention. We are open for any MLOps-related questions.",
        }
    ];
}

export default function MLOpsPresentationPage() {
    return <Presentation slides={buildSlides()} />;
}
