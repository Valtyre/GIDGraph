import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { Infobox } from "./infobox";
import { Graph } from "../page";
import { buildApiUrl } from "../../lib/apiConfig";

export default function NatrualLanguageBox({ fun, graph }: { fun: Dispatch<SetStateAction<Graph | null>>, graph: Graph | null }) {
  const [text, setText] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [graphModified, setGraphModified] = useState(false);
  const [selectedExample, setSelectedExample] = useState<string>("");

  const exampleText1 = "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling. NOTCH activates NOTCH."
  const exampleText2 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1."
  const exampleText3 = "ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background, promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression, as probed with a reporter line, is lost in the QC and CEI cells in jkd mutants from the early heart stage onward. The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant. The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR. SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background. The post-embryonic expression of JKD is reduced in shr mutant roots. The post-embryonic expression of JKD is reduced in scr mutant roots. WOX5 is not expressed in scr mutants. WOX5 expression is reduced in shr mutants. WOX5 expression is rarely detected in mp or bdl mutants. The PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 &2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos. Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF, stabilizing the dimerization that represses ARF transcriptional activity. Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation. Wild-type root, treated with CLE40p, shows a reduction of WOX5 expression, whereas in cle40 loss-of-function plants, WOX5 is overexpressed."
  const initialGraph = useRef<Graph | null>(null);

  // Save the first loaded graph
  useEffect(() => {
    if (graph && initialGraph.current === null) {
      initialGraph.current = graph;
    }
  }, [graph]);

  // Check if graph has changed - only show warning if there's actual content
  useEffect(() => {
    // Don't show warning if both text and graph are empty
    if (!text.trim() && (!graph || graph.edges.length === 0)) {
      setGraphModified(false);
      return;
    }
    
    if (graph && initialGraph.current) {
      const same = JSON.stringify(graph) === JSON.stringify(initialGraph.current);
      setGraphModified(!same);
    }
  }, [graph, text]);

  async function fetchGraph(nlText: string) {
    setIsParsing(true);
    document.body.style.cursor = "wait";

    try {
      const res = await fetch(buildApiUrl("/api/parse"), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: nlText }),
      });

      const data: { graph: Graph } = await res.json();

      let nextId = 0;
      const withIds = data.graph.edges.map(edge =>
        edge.id === undefined ? { ...edge, id: nextId++ } : edge
      );

      fun({ node: data.graph.node, edges: withIds });
    } catch (err: any) {
      console.error('parse API error:', err);
      const reason = err.message || err.toString();
      alert(`Failed to fetch graph data: ${reason}. Please try again.`);
    } finally {
      setIsParsing(false);
      document.body.style.cursor = "default";
    }
  }

  async function optimizeText() {
    setIsOptimizing(true);
    document.body.style.cursor = "wait";

    try {
      const res = await fetch(buildApiUrl("/api/optimize_nl"), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      const data: { text: string; optimized: boolean; fallback: boolean } = await res.json();
      setText(data.text);
    } catch (err: any) {
      console.error('optimize API error:', err);
      const reason = err.message || err.toString();
      alert(`Failed to optimize text: ${reason}. The original text has been kept.`);
    } finally {
      setIsOptimizing(false);
      document.body.style.cursor = "default";
    }
  }

  function handleExampleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const val = e.target.value;
    setSelectedExample(val);
    if (val === "") {setText("")}
    if (val === "1") setText(exampleText1);
    else if (val === "2") setText(exampleText2);
    else if (val === "3") setText(exampleText3);
  }

  const info = `
  Input natural language discriptions of gene interactions into this field. 
  From here, the interactions can be extracted, and displayed in the Semi-Natural Language box.
  `

  return (
    <section
      role="region"
      aria-labelledby="nl-form-title"
      className="flex flex-col w-full h-full p-5 lg:p-6 overflow-hidden"
    >
      {/* Section heading */}
      <h2
        id="nl-form-title"
        className="section-heading text-2xl lg:text-3xl"
      >
        Gene Interaction Description
        <Infobox text={info}/>
      </h2>

      {/* Warning banner when graph is modified */}
      {graphModified && (
        <div 
          role="alert"
          className="flex items-center gap-2 px-4 py-3 mb-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800"
        >
          <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span className="text-sm font-medium">
            The natural language may not match the graph output
          </span>
        </div>
      )}

      {/* Text input area */}
      <textarea
        className={`
          w-full flex-1 min-h-[100px]
          p-4 
          bg-off border-2 border-third/30 
          rounded-lg
          text-foreground placeholder:text-gray-400
          resize-none
          transition-all duration-200
          hover:border-third/50
          focus:border-third focus:ring-2 focus:ring-third/20 focus:outline-none
          ${(isParsing || isOptimizing) ? "cursor-wait opacity-75" : ""}
        `}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter gene interaction descriptions here..."
        aria-describedby={graphModified ? "graph-warning" : undefined}
        disabled={isParsing || isOptimizing}
      />

      {/* Actions row */}
      <div className="flex flex-col sm:flex-row gap-3 justify-between items-stretch sm:items-center mt-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={optimizeText}
            disabled={isParsing || isOptimizing || !text.trim()}
            className={`
              btn
              px-5 py-2.5
              text-sm sm:text-base
              border border-third/30
              disabled:opacity-50 disabled:cursor-not-allowed
              ${(isParsing || isOptimizing) ? "cursor-wait" : ""}
            `}
            aria-busy={isOptimizing}
          >
            {isOptimizing ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Optimizing...
              </>
            ) : (
              "Optimize for Parser"
            )}
          </button>

          <button
            onClick={() => {
              fetchGraph(text);
            }}
            disabled={isParsing || isOptimizing || !text.trim()}
            className={`
              btn btn-primary
              px-5 py-2.5
              text-sm sm:text-base
              disabled:opacity-50 disabled:cursor-not-allowed
              ${(isParsing || isOptimizing) ? "cursor-wait" : ""}
            `}
            aria-busy={isParsing}
          >
            {isParsing ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </>
            ) : (
              "Convert to Semi-Natural Language"
            )}
          </button>
        </div>

        {/* Example selector */}
        <div className="flex items-center gap-3">
          <label
            htmlFor="example-select"
            className="text-sm font-semibold text-foreground whitespace-nowrap"
          >
            Examples:
          </label>
          <select
            id="example-select"
            value={selectedExample}
            onChange={handleExampleChange}
            disabled={isParsing || isOptimizing}
            className="
              px-3 py-2
              bg-third text-white 
              font-medium text-sm
              rounded-lg
              border-0
              cursor-pointer
              transition-colors duration-150
              hover:bg-dark
              focus:ring-2 focus:ring-third/50 focus:ring-offset-2 focus:outline-none
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            <option value="">Select...</option>
            <option value="1">Example case</option>
            <option value="2">Molecular mechanisms</option>
            <option value="3">Single-cell niche</option>
          </select>
        </div>
      </div>
    </section>
  );
}
