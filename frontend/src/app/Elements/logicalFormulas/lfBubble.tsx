import { LogicalFormula } from "./lfContainer";

type ToggleFn = (targetGene: string, idx: number) => void;

type LogicalFormulasBubbleProps = {
  lf: LogicalFormula;
  geneColors: Record<string, string>;
  onToggle: ToggleFn;
};

export default function LogicalFormulasBubble({
  lf,
  geneColors,
  onToggle,
}: LogicalFormulasBubbleProps) {
  const geneColor = geneColors[lf.targetGene] ?? "#b9c0cb";

  return (
    <div
      className="rounded-[1.35rem] border border-[color:var(--color-line)] bg-[rgba(255,255,255,0.82)] p-4 shadow-[0_10px_28px_rgba(27,38,54,0.08)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_18px_40px_rgba(27,38,54,0.12)]"
      style={{ boxShadow: `inset 3px 0 0 ${geneColor}, 0 10px 28px rgba(27,38,54,0.08)` }}
      role="listitem"
    >
      <div className="mb-3 flex items-center gap-3">
        <span className="inline-flex rounded-full px-3 py-1 text-xs font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-accent-strong)]" style={{ backgroundColor: `${geneColor}55` }}>
          Target
        </span>
        <span className="font-[family:var(--font-display)] text-3xl leading-none text-foreground">
          {lf.targetGene}
        </span>
      </div>

      <div className="rounded-[1.15rem] border border-[color:var(--color-line)] bg-[rgba(246,242,234,0.7)] px-3 py-3 text-sm text-[color:var(--color-ink-soft)]">
        <div className="mb-2 text-[0.72rem] font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-accent-strong)]">
          Formula
        </div>
        <span className="inline-flex flex-wrap items-center gap-2">
          {lf.incomingGenes.map((ig, idx) => {
            const hasNext = idx < lf.incomingGenes.length - 1;
            const badgeColor = geneColors[ig.gene] ?? "#d7dce4";

            return (
              <span key={idx} className="inline-flex items-center">
                <span
                  className="inline-flex items-center rounded-full border border-white/70 px-3 py-1.5 text-xs font-bold text-[color:var(--color-ink)] shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]"
                  style={{ backgroundColor: badgeColor }}
                >
                  {!ig.label && <span className="mr-1 text-[color:var(--color-danger)]">NOT</span>}
                  {ig.gene}
                </span>

                {hasNext && (
                  <button
                    onClick={() => onToggle(lf.targetGene, idx)}
                    className={`mx-2 rounded-full px-3 py-1 text-[0.68rem] font-extrabold uppercase tracking-[0.14em] transition-all duration-150 ${
                      ig.truthValue
                        ? "bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent-strong)]"
                        : "bg-[rgba(36,46,64,0.08)] text-[color:var(--color-ink-soft)]"
                    }`}
                    aria-label={`Toggle connector, currently ${ig.truthValue ? 'AND' : 'OR'}`}
                    title="Click to toggle between AND and OR"
                  >
                    {ig.truthValue ? "AND" : "OR"}
                  </button>
                )}
              </span>
            );
          })}
        </span>
      </div>
    </div>
  );
}
