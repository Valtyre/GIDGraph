import { Dispatch, SetStateAction, useState } from "react";
import { Infobox } from "./infobox";
import { Graph } from "../page";

export default function NatrualLanguageBox({ fun } : { fun: Dispatch<SetStateAction<Graph | null>>}) {
  const [text, setText] = useState("");

  const [cursor, setCursor] = useState<"default" | "wait">("default");


  async function fetchGraph(nlText: string) {
    // Set cursor to "wait"
    setCursor("wait")
    document.body.style.cursor = "wait";

  
    try {
      const res = await fetch('http://localhost:8000/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: nlText }),
      });
  
      const data: { graph: Graph } = await res.json();
  
      /* ensure every edge has a stable numeric id */
      let nextId = 0;
      const withIds = data.graph.edges.map(edge =>
        edge.id === undefined ? { ...edge, id: nextId++ } : edge
      );
  
      fun({ node: data.graph.node, edges: withIds });
  
    } catch (err) {
      console.error('parse API error:', err);
  
    } finally {
      setCursor("default")
      document.body.style.cursor = "default";

    }
  }

  const info = `
  Input natural language discriptions of gene interactions into this field. 
  From here, the interactions can be extracted, and diplayed in the Semi-Natural Language box.
  `

  return (
    <>
      <div className="flex flex-col mx-auto w-full p-5"> 
        <h1 className=" font-bold text-3xl text-second">
          Gene Interaction Description <Infobox text={info}/>
        </h1>
        <textarea
          className= {`bg-off border-third border-2 rounded-sm w-full p-3 h-full resize-none hover:cursor-${cursor}`}
          value={text} 
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here"
        />
        <button 
          onClick={() => {
            fetchGraph(text); 
            console.log("click")
          }} 
          className={`bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main hover:cursor-${cursor} hover:bg-second `}>
          Convert to Semi-Natural Language
        </button>
      </div>
    </>
  );
}
