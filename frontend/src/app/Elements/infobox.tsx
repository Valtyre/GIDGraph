export function Infobox({ text }: { text: string }) {
  return (
    <div className="group relative inline-flex items-center" tabIndex={0}>
      <span
        className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[color:var(--color-line)] bg-white/75 text-sm font-bold text-[color:var(--color-accent-strong)] shadow-[0_8px_20px_rgba(31,95,114,0.08)] transition-all duration-200 group-hover:-translate-y-0.5 group-hover:border-[color:rgba(31,95,114,0.28)] group-hover:bg-white group-focus-within:border-[color:rgba(31,95,114,0.28)] group-focus-within:bg-white"
        aria-label="More information"
      >
        ?
      </span>

      <aside
        role="tooltip"
        className="pointer-events-none absolute right-0 top-[calc(100%+0.8rem)] z-30 w-72 rounded-[1.1rem] border border-[color:var(--color-line)] bg-[rgba(255,252,247,0.97)] px-4 py-3 text-sm leading-relaxed text-[color:var(--color-ink-soft)] opacity-0 shadow-[0_24px_60px_rgba(28,40,58,0.18)] transition-all duration-200 group-hover:pointer-events-auto group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:translate-y-0 group-focus-within:opacity-100 lg:w-80"
      >
        <p>{text}</p>
      </aside>
    </div>
  );
}
