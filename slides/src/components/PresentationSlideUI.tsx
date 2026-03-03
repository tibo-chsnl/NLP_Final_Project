import React from "react";

export interface Slide {
    tag: string;
    tagColor: string;
    title: string;
    content: React.ReactNode;
    notes: string;
}

export function DiagramFlow({ items }: { items: string[] }) {
    return (
        <div className="flex flex-wrap items-center justify-center gap-2 my-4">
            {items.map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                    <div className="diagram-box">{item}</div>
                    {i < items.length - 1 && <div className="diagram-arrow">→</div>}
                </div>
            ))}
        </div>
    );
}

export function DiagramFlowVertical({ items }: { items: { label: string; sub?: string }[] }) {
    return (
        <div className="flex flex-col items-center gap-1 my-3">
            {items.map((item, i) => (
                <div key={i} className="flex flex-col items-center gap-1 w-full max-w-xs">
                    <div className="diagram-box w-full">
                        <div>{item.label}</div>
                        {item.sub && <div className="text-[10px] text-slate-400 mt-0.5">{item.sub}</div>}
                    </div>
                    {i < items.length - 1 && <div className="diagram-arrow rotate-90">→</div>}
                </div>
            ))}
        </div>
    );
}

export function Table({ headers, rows, highlight }: { headers: string[]; rows: string[][]; highlight?: number }) {
    return (
        <table className="slide-table">
            <thead>
                <tr>{headers.map((h, i) => <th key={i}>{h}</th>)}</tr>
            </thead>
            <tbody>
                {rows.map((row, i) => (
                    <tr key={i} className={i === highlight ? "!bg-indigo-500/10" : ""}>
                        {row.map((cell, j) => (
                            <td key={j} className={i === highlight ? "!text-indigo-300 !font-semibold" : ""}>
                                {cell}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export function Bullet({ children, icon = "→" }: { children: React.ReactNode; icon?: string }) {
    return (
        <div className="flex gap-2 items-start mb-2">
            <span className="text-indigo-400 text-sm mt-0.5 shrink-0">{icon}</span>
            <span className="text-slate-300 text-sm leading-relaxed">{children}</span>
        </div>
    );
}

export function SectionLabel({ children, color = "indigo" }: { children: React.ReactNode; color?: string }) {
    const colors: Record<string, string> = {
        indigo: "text-indigo-400 border-indigo-500/20",
        emerald: "text-emerald-400 border-emerald-500/20",
        amber: "text-amber-400 border-amber-500/20",
        purple: "text-purple-400 border-purple-500/20",
    };
    return (
        <div className={`text-[10px] font-semibold uppercase tracking-widest mb-3 pb-2 border-b ${colors[color]}`}>
            {children}
        </div>
    );
}
