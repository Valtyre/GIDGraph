import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { Infobox } from "./infobox";
import { Graph } from "../page";

export default function NatrualLanguageBox({ fun, graph }: { fun: Dispatch<SetStateAction<Graph | null>>, graph: Graph | null }) {
  const [text, setText] = useState("");
  const [cursor, setCursor] = useState<"default" | "wait">("default");
  const [graphModified, setGraphModified] = useState(false);

  const exampleText1 = "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling. NOTCH activates NOTCH."
  const exampleText2 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1."
  const exampleText3 = "The expression of SCR is reduced in shr mutants. ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression as probed with a reporter lines is lost in the QC and CEI cells in jkd mutants from the early heart stage onward."
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

  const info = `
  Input natural language discriptions of gene interactions into this field. 
  From here, the interactions can be extracted, and displayed in the Semi-Natural Language box.
  `

  return (
    <>
      <div className="flex flex-col mx-auto w-full p-5">
        <h1 className="font-bold text-3xl text-third">
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
        <div className="flex flex-row gap-2 justify-between w-full">
            <button
              onClick={() => {
                fetchGraph(text);
                console.log("click");
              }}
              className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main ${cursor === "wait" ? "cursor-wait" : "cursor-default"} hover:bg-dark`}
              >
              Convert to Semi-Natural Language
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setText(exampleText1)
                }}
                className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main ${cursor === "wait" ? "cursor-wait" : "cursor-default"} hover:bg-dark`}
                >
                Example 1
              </button>
              <button
                onClick={() => {
                  setText(exampleText2)
                }}
                className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main ${cursor === "wait" ? "cursor-wait" : "cursor-default"} hover:bg-dark`}
                >
                Example 2
              </button>
              <button
                onClick={() => {
                  setText(exampleText3)
                }}
                className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main ${cursor === "wait" ? "cursor-wait" : "cursor-default"} hover:bg-dark`}
                >
                Example 2
              </button>
                </div>
          </div>
      </div>
    </>
  );
}
