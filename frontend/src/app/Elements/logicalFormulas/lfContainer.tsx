import { Infobox } from "../infobox";
import LogicalFormulasBubble from "./lfBubble";
import ExportButton from "./ExportButton"; 

/* ----- types (unchanged) ----- */
export type incomingGene = {
  gene: string;
  label: boolean;        // activation / inhibition
  truthValue: boolean;   // true = AND, false = OR
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
};

export default function LogicalFormulasContainer({lf, setLF, geneColors, onExport, isExporting = false}: LogicalFormulasContainerProps) {
  /* toggle function passed down to each bubble */
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

  const info = `
  In this field, the logical formulas derived from the gene interactions is shown. Click the 'AND' and 'OR' buttons to switch between.
  The user can export these logical formulas to GINML, for use in GinSim.`;

  return (
    <section
      className="flex flex-col gap-4 p-4 lg:p-5"
      role="region"
      aria-labelledby="lf-title"
    >
      <h2 id="lf-title" className="section-heading text-2xl lg:text-3xl">
        Logical Formulas
        <Infobox text={info} />
      </h2>

      {lf.length === 0 ? (
        <div className="text-center text-gray-500 py-8 bg-off/50 rounded-lg">
          <svg 
            className="w-12 h-12 mx-auto mb-3 text-gray-300" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No logical formulas yet</p>
          <p className="text-sm mt-1">Convert text above to generate formulas</p>
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-3" role="list" aria-label="Logical formulas">
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
