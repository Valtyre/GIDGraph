import LogicalFormulasBubble from "./lfBubble";

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
  geneColors,                       // <‑‑ NEW
}: {
  lf: LogicalFormula[];
  setLF: React.Dispatch<React.SetStateAction<LogicalFormula[]>>;
  geneColors: Record<string, string>;  //
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

  if (!lf.length)
    return (
      <div className="text-center text-gray-400 mt-4">
        No logical formulas yet
      </div>
    );

  return (
    <div className="flex flex-col gap-2 p-4">
      {lf.map((formula, idx) => (
        <LogicalFormulasBubble
          key={idx}
          lf={formula}
          geneColors={geneColors} 
          onToggle={toggleConnector}
        />
      ))}
    </div>
  );
}
