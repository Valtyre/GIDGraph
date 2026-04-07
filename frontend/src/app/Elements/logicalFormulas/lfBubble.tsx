import { LogicalFormula } from "./lfContainer";

type ToggleFn = (targetGene: string, idx: number) => void;

type LogicalFormulasBubbleProps = {
  lf: LogicalFormula;
  geneColors: Record<string, string>;
  onToggle: ToggleFn;
};

export default function LogicalFormulasBubble({lf, geneColors, onToggle}: LogicalFormulasBubbleProps) {
  const geneColor = geneColors[lf.targetGene] ?? "#9ca3af"; 

  return (
    <div
      className="
        bg-second text-foreground 
        px-4 py-3 
        rounded-lg 
        shadow-sm
        border-l-4
        transition-shadow duration-200
        hover:shadow-md
      "
      style={{ borderLeftColor: geneColor }}
      role="listitem"
    >
      <span className="font-bold text-lg">{lf.targetGene}</span>
      <span className="text-gray-500 mx-2">=</span>
      
      <span className="inline-flex flex-wrap items-center gap-1">
        {lf.incomingGenes.map((ig, idx) => {
          const hasNext = idx < lf.incomingGenes.length - 1;
          const badgeColor = geneColors[ig.gene] ?? "#d1d5db";

          return (
            <span key={idx} className="inline-flex items-center">
              {/* Gene badge */}
              <span
                className="
                  inline-flex items-center
                  rounded-full px-2.5 py-1 
                  text-xs font-semibold 
                  text-gray-800
                  transition-transform duration-150
                  hover:scale-105
                "
                style={{ backgroundColor: badgeColor }}
              >
                {ig.label ? "" : <span className="mr-0.5">¬</span>}
                {ig.gene}
              </span>

              {/* AND/OR toggle button */}
              {hasNext && (
                <button
                  onClick={() => onToggle(lf.targetGene, idx)}
                  className={`
                    mx-2 px-3 py-1 
                    rounded-md 
                    text-xs font-bold
                    uppercase tracking-wide
                    transition-all duration-150
                    ${ig.truthValue 
                      ? "bg-third/20 text-third hover:bg-third/30" 
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                    }
                  `}
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
  );
}
