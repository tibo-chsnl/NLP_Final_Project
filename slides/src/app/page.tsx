import Link from "next/link";

export default function Home() {
    return (
        <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-[#08080f] select-none">
            {/* Background Animations */}
            <div className="fixed top-[-200px] left-[-100px] w-[600px] h-[600px] rounded-full bg-indigo-900/30 blur-[150px] animate-float" />
            <div
                className="fixed bottom-[-200px] right-[-100px] w-[600px] h-[600px] rounded-full bg-purple-900/25 blur-[150px] animate-float"
                style={{ animationDelay: "3s" }}
            />
            <div
                className="fixed top-[40%] right-[20%] w-[400px] h-[400px] rounded-full bg-emerald-900/15 blur-[120px] animate-float"
                style={{ animationDelay: "5s" }}
            />

            <div className="relative z-10 text-center mb-12 animate-fade-in-up">
                <h1 className="text-5xl md:text-6xl font-bold mb-4">
                    <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
                        Final Project
                    </span>
                    <br />
                    <span className="text-white/90">Presentations</span>
                </h1>
                <p className="text-slate-500 text-lg max-w-md mx-auto mb-8">
                    Select a presentation track below.
                </p>

                <div className="flex flex-col md:flex-row items-center justify-center gap-6">
                    {/* NLP Portal */}
                    <Link
                        href="/nlp"
                        className="group relative flex flex-col items-center justify-center w-64 h-48 glass rounded-2xl hover:bg-white/5 border border-indigo-500/20 hover:border-indigo-400/50 transition-all duration-300 overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <h2 className="text-2xl font-bold text-white mb-2 group-hover:scale-105 transition-transform">
                            NLP
                        </h2>
                        <span className="badge badge-indigo">Model Architecture</span>
                        <div className="absolute bottom-4 right-4 text-indigo-400 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">
                            →
                        </div>
                    </Link>

                    {/* MLOps Portal */}
                    <Link
                        href="/mlops"
                        className="group relative flex flex-col items-center justify-center w-64 h-48 glass rounded-2xl hover:bg-white/5 border border-emerald-500/20 hover:border-emerald-400/50 transition-all duration-300 overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <h2 className="text-2xl font-bold text-white mb-2 group-hover:scale-105 transition-transform">
                            MLOps
                        </h2>
                        <span className="badge badge-emerald">Deployment & Tracking</span>
                        <div className="absolute bottom-4 right-4 text-emerald-400 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">
                            →
                        </div>
                    </Link>
                </div>
            </div>

            <p className="relative z-10 mt-12 text-[11px] text-slate-700 font-mono tracking-widest">
                M2 EFREI — MARCH 2026
            </p>
        </div>
    );
}
