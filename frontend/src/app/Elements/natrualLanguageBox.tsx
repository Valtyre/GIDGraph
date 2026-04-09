import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { Infobox } from "./infobox";
import { Graph } from "../page";
import { buildApiUrl } from "../../lib/apiConfig";

type NaturalLanguageBoxProps = {
  fun: Dispatch<SetStateAction<Graph | null>>;
  graph: Graph | null;
  isParsing: boolean;
  isOptimizing: boolean;
  setIsParsing: Dispatch<SetStateAction<boolean>>;
  setIsOptimizing: Dispatch<SetStateAction<boolean>>;
};

export default function NatrualLanguageBox({
  fun,
  graph,
  isParsing,
  isOptimizing,
  setIsParsing,
  setIsOptimizing,
}: NaturalLanguageBoxProps) {
  const [text, setText] = useState("");
  const [graphModified, setGraphModified] = useState(false);
  const [selectedExample, setSelectedExample] = useState<string>("");
  const initialGraph = useRef<Graph | null>(null);

  const exampleText1 =
    "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling. NOTCH activates NOTCH.";
  const exampleText2 =
    "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1.";
  const exampleText3 =
    "ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background, promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression, as probed with a reporter line, is lost in the QC and CEI cells in jkd mutants from the early heart stage onward. The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant. The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR. SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background. The post-embryonic expression of JKD is reduced in shr mutant roots. The post-embryonic expression of JKD is reduced in scr mutant roots. WOX5 is not expressed in scr mutants. WOX5 expression is reduced in shr mutants. WOX5 expression is rarely detected in mp or bdl mutants. The PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 &2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos. Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF, stabilizing the dimerization that represses ARF transcriptional activity. Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation. Wild-type root, treated with CLE40p, shows a reduction of WOX5 expression, whereas in cle40 loss-of-function plants, WOX5 is overexpressed.";

  useEffect(() => {
    if (graph && initialGraph.current === null) {
      initialGraph.current = graph;
    }
  }, [graph]);

  useEffect(() => {
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
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: nlText }),
      });

      const data = await res.json();
      if (!res.ok) {
        const message =
          data?.detail?.message || data?.message || "Unable to parse the provided text.";
        throw new Error(message);
      }

      const graphData: Graph = data.graph;
      let nextId = 0;
      const withIds = graphData.edges.map((edge) =>
        edge.id === undefined ? { ...edge, id: nextId++ } : edge
      );

      fun({ node: graphData.node ?? "", edges: withIds });
    } catch (err: any) {
      console.error("parse API error:", err);
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
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data: { text: string; optimized: boolean; fallback: boolean } = await res.json();
      setText(data.text);
    } catch (err: any) {
      console.error("optimize API error:", err);
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

    if (val === "") setText("");
    else if (val === "1") setText(exampleText1);
    else if (val === "2") setText(exampleText2);
    else if (val === "3") setText(exampleText3);
  }

  const info =
    "Write or paste a description of the regulatory system. The parser turns the text into structured interactions.";

  return (
    <section
      role="region"
      aria-labelledby="nl-form-title"
      className="glass-panel workspace-panel animate-enter flex h-[560px] flex-col"
    >
      <div className="panel-header">
        <div>
          <span className="eyebrow">Step 1</span>
          <div className="section-heading mt-4">
            <div>
              <h2 id="nl-form-title" className="panel-title">
                Source text
              </h2>
              <p className="panel-subtitle">
                Paste or write the input text.
              </p>
            </div>
            <Infobox text={info} />
          </div>
        </div>

        <div className="hidden rounded-[1.2rem] border border-[color:var(--color-line)] bg-white/55 px-4 py-3 text-right lg:block">
          <p className="text-[0.72rem] font-extrabold uppercase tracking-[0.16em] text-[color:var(--color-accent-strong)]">
            Input
          </p>
          <p className="mt-1 text-sm text-[color:var(--color-ink-soft)]">
            Natural language
          </p>
        </div>
      </div>

      {graphModified && (
        <div
          role="alert"
          className="mb-4 flex items-start gap-3 rounded-[1.25rem] border border-[color:rgba(153,111,45,0.24)] bg-[color:var(--color-warning-soft)] px-4 py-3 text-[color:var(--color-warning)]"
        >
          <span className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-white/70 text-sm font-bold">
            !
          </span>
          <div>
            <p className="font-semibold">Graph edits no longer match the text exactly.</p>
            <p className="text-sm opacity-80">
              The graph has been edited after parsing.
            </p>
          </div>
        </div>
      )}

      <textarea
        className={`workspace-input custom-scrollbar min-h-[290px] flex-1 resize-none px-5 py-5 text-[0.98rem] leading-7 ${
          isParsing || isOptimizing ? "cursor-wait opacity-75" : ""
        }`}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Describe how genes activate, inhibit, or regulate one another."
        aria-describedby={graphModified ? "graph-warning" : undefined}
        disabled={isParsing || isOptimizing}
      />

      <div className="mt-5 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            onClick={optimizeText}
            disabled={isParsing || isOptimizing || !text.trim()}
            className={`btn btn-secondary min-w-[190px] ${isParsing || isOptimizing ? "cursor-wait" : ""}`}
            aria-busy={isOptimizing}
          >
            {isOptimizing ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Refining text
              </>
            ) : (
              "Refine for parser"
            )}
          </button>

          <button
            onClick={() => fetchGraph(text)}
            disabled={isParsing || isOptimizing || !text.trim()}
            className={`btn btn-primary min-w-[240px] ${isParsing || isOptimizing ? "cursor-wait" : ""}`}
            aria-busy={isParsing}
          >
            {isParsing ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Building graph
              </>
            ) : (
              "Convert to structured network"
            )}
          </button>
        </div>

        <div className="w-full max-w-sm">
          <label
            htmlFor="example-select"
            className="mb-2 block text-[0.78rem] font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-accent-strong)]"
          >
            Examples
          </label>
          <select
            id="example-select"
            value={selectedExample}
            onChange={handleExampleChange}
            disabled={isParsing || isOptimizing}
            className="workspace-select h-[3.1rem] px-4"
          >
            <option value="">Choose an example</option>
            <option value="1">Example case</option>
            <option value="2">Molecular mechanisms</option>
            <option value="3">Single-cell niche</option>
          </select>
        </div>
      </div>
    </section>
  );
}
