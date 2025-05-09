import { Infobox } from "../infobox";
import LogicalFormulasBubble from "./lfBubble";
import ExportButton from "./ExportButton"; // Import the new ExportButton component

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
/* ----------------------------- */

export default function LogicalFormulasContainer({
  lf,
  setLF,
  geneColors,
  onExport,
}: {
  lf: LogicalFormula[];
  setLF: React.Dispatch<React.SetStateAction<LogicalFormula[]>>;
  geneColors: Record<string, string>;
  onExport: () => void;
}) {
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
  In this field, the logical formulas derived from the gene interactions is shown. Click the 'and' and 'or' buttons to switch between.
  The user can export these logical formulas to GINML, for use in GinSim.
  `;

  if (!lf.length)
    return (
      <>
        <h1 className="font-bold text-3xl text-third">
          Logical Formulas
          <Infobox text={info} />
        </h1>
        <div className="text-center text-gray-400 mt-4">
          No logical formulas yet
        </div>
      </>
    );

  return (
    <div className="flex flex-col gap-2 p-4">
      <h1 className="font-bold text-3xl text-third">
        Logical Formulas
        <Infobox text={info} />
      </h1>
      {lf.map((formula, idx) => (
        <LogicalFormulasBubble
          key={idx}
          lf={formula}
          geneColors={geneColors}
          onToggle={toggleConnector}
        />
      ))}
      {lf.length > 0 && <ExportButton onExport={onExport} />} {/* Conditionally render ExportButton */}
    </div>
  );
}
