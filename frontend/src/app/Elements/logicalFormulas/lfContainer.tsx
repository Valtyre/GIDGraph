import { Infobox } from "../infobox";
import LogicalFormulasBubble from "./lfBubble";
import ExportButton from "./ExportButton";

export type incomingGene = {
  gene: string;
  label: boolean;
  truthValue: boolean;
};

export type LogicalFormula = {
  targetGene: string;
  incomingGenes: incomingGene[];
};

type LogicalFormulasContainerProps = {
  lf: LogicalFormula[];
  setLF: React.Dispatch<React.SetStateAction<LogicalFormula[]>>;
  geneColors: Record<string, string>;
  onExport: () => void;
  isExporting?: boolean;
  hasGraph?: boolean;
};

export default function LogicalFormulasContainer({
  lf,
  setLF,
  geneColors,
  onExport,
  isExporting = false,
  hasGraph = false,
}: LogicalFormulasContainerProps) {
  const toggleConnector = (targetGene: string, idx: number) => {
    setLF((prev) =>
      prev.map((formula) =>
        formula.targetGene === targetGene
          ? {
              ...formula,
              incomingGenes: formula.incomingGenes.map((ig, igIdx) =>
                igIdx === idx ? { ...ig, truthValue: !ig.truthValue } : ig
              ),
            }
          : formula
      )
    );
  };

  const info = "Logical formulas are derived from the current interaction set.";

  return (
    <section
      className="glass-panel workspace-panel flex h-[640px] flex-col"
      role="region"
      aria-labelledby="lf-title"
    >
      <div className="panel-header">
        <div>
          <span className="eyebrow">Step 4</span>
          <div className="section-heading mt-4">
            <div>
              <h2 id="lf-title" className="panel-title">
                Logical formulas
              </h2>
              <p className="panel-subtitle">
                Review and export formulas.
              </p>
            </div>
            <Infobox text={info} />
          </div>
        </div>
      </div>

      {lf.length === 0 ? (
        <div className="empty-state flex-1">
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[color:var(--color-line)] bg-white/85">
            <svg
              className="h-7 w-7 text-[color:var(--color-accent-strong)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-lg font-semibold text-foreground">No formulas yet.</p>
          <p className="max-w-sm text-sm">
            {hasGraph
              ? "Add or adjust interactions to continue."
              : "Generate a graph to derive formulas."}
          </p>
        </div>
      ) : (
        <>
          <div className="custom-scrollbar flex h-full flex-1 flex-col gap-3 overflow-y-auto pr-1" role="list" aria-label="Logical formulas">
            {lf.map((formula, idx) => (
              <LogicalFormulasBubble
                key={idx}
                lf={formula}
                geneColors={geneColors}
                onToggle={toggleConnector}
              />
            ))}
          </div>
          <ExportButton onExport={onExport} isLoading={isExporting} />
        </>
      )}
    </section>
  );
}
