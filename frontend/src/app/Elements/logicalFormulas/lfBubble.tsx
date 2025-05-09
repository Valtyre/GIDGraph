import { LogicalFormula } from "./lfContainer";

type ToggleFn = (targetGene: string, idx: number) => void;

export default function LogicalFormulasBubble({
  lf,
  geneColors,
  onToggle,
}: {
  lf: LogicalFormula;
  geneColors: Record<string, string>;
  onToggle: ToggleFn;
}) {
  /* colour for target gene */
  const geneColor = geneColors[lf.targetGene] ?? "#9ca3af"; // Tailwind gray‑400 fallback

  return (
    <div
      className="bg-gray-100 text-gray-900 px-3 py-2 rounded shadow mb-1"
      style={{ border: `5px solid ${geneColor}` }}      /* ← coloured border */
    >
      <span className="font-bold">{lf.targetGene}</span>{" = "}
      {lf.incomingGenes.map((ig, idx) => {
        const hasNext = idx < lf.incomingGenes.length - 1;
        const badgeColor = geneColors[ig.gene] ?? "#d1d5db";

        return (
          <span key={idx} className="inline-flex items-center">
            {/* coloured badge for each regulator */}
            <span
              className="rounded-full px-2 py-0.5 text-xs font-semibold mr-1 text-gray-900"
              style={{ backgroundColor: badgeColor }}
            >
              {ig.label ? "" : "¬"} {ig.gene}
            </span>

            {hasNext && (
              <button
                onClick={() => onToggle(lf.targetGene, idx)}
                className={`mx-1 px-3 py-1 rounded-md text-xs font-semibold
                  bg-gray-400 hover:bg-gray-500
                  ${ig.truthValue ? "text-black" : "text-white"}`}
              >
                {ig.truthValue ? "AND" : "OR"}
              </button>
            )}
          </span>
        );
      })}
    </div>
  );
}
