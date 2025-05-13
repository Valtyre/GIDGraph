import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { Infobox } from "./infobox";
import { Graph } from "../page";

export default function NatrualLanguageBox({ fun, graph }: { fun: Dispatch<SetStateAction<Graph | null>>, graph: Graph | null }) {
  const [text, setText] = useState("");
  const [cursor, setCursor] = useState<"default" | "wait">("default");
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

  // Check if graph has changed
  useEffect(() => {
    if (graph && initialGraph.current) {
      const same = JSON.stringify(graph) === JSON.stringify(initialGraph.current);
      setGraphModified(!same);
    }
  }, [graph]);

  async function fetchGraph(nlText: string) {
    setCursor("wait");
    document.body.style.cursor = "wait";

    try {
      const res = await fetch("https://api.gidgraph.com/api/parse", {
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
      setCursor("default");
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
    <>
      {/* 1. form region */}
      <div
        role="form"
        aria-labelledby="nl-form-title"
        className="flex flex-col mx-auto w-full p-5"
      >
        {/* 2. heading with id */}
        <h1
          id="nl-form-title"
          className="font-bold text-3xl text-third"
        >
          Gene Interaction Description <Infobox text={info}/>
        </h1>

        {graphModified && (
          <h2 className="text-lg font-bold text-red-600">
            ⚠️ Warning: The natural language does not match the graph output 
          </h2>
        )}

        <textarea
          className={`bg-off border-third border-2 text-black rounded-sm w-full p-3 h-full resize-none ${cursor === "wait" ? "cursor-wait" : "cursor-default"}`}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here"
        />

        {/* 3. examples as a group */}
        <div
          role="group"
          aria-labelledby="example-select-label"
          className="flex flex-row gap-2 justify-between w-full"
        >
          <button
            onClick={() => {
              fetchGraph(text);
              console.log("click");
            }}
            className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-white ${cursor === "wait" ? "cursor-wait" : "cursor-default"} hover:bg-dark`}
          >
            Convert to Semi-Natural Language
          </button>
          <div className="flex items-center gap-2">
            <label
              id="example-select-label"
              htmlFor="example-select"
              className="font-bold text-black"
            >
              Examples:
            </label>
            <select
              id="example-select"
              value={selectedExample}
              onChange={handleExampleChange}
              tabIndex={0}
              aria-labelledby="example-select-label"
              className="bg-third text-white font-bold rounded-sm p-2 border-2 border-third w-[150px] whitespace-pre-line focus:ring-2 focus:ring-offset-2 focus:ring-third"
            >
              <option value="">{`Select...`}</option>
              <option value="1">{`Example case`}</option>
              <option value="2">{`Molecular mechanisms … approach`}</option>
              <option value="3">{`Single-cell and coupled … niche`}</option>
            </select>
          </div>
        </div>
      </div>
    </>
  );
}