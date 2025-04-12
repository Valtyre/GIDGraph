'use client'
import { useState } from "react";
import TopBar from "./Elements/TopBar";
import { Interaction, SNLBox } from "./Elements/SNL/snlBox";
import NatrualLanguageBox from "./Elements/natrualLanguageBox";
import GeneNetworkGraph from "./graph";

export type Graph = {
  edges: Interaction[],
  node: string
}

export default function Home() {
  const [graph, setGraph] = useState<Graph | null>(null);
  const emptyG: Graph = {node: "", edges: []}

  function getSNL(str: string) {
    fetch("http://localhost:8000/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: `"${str}"` }),
    })
      .then(response => response.json())
      .then((data: { graph: Graph }) => {
        setGraph(data.graph);
        console.log("Graph edges:", data.graph.edges);
      })
      .catch(error => {
        console.error("Error fetching SNL data:", error);
      });
  }

  return (
    <div>
      <TopBar />
      <div className="flex flex-row bg-blue-950 p-5 h-[400px]">
        <NatrualLanguageBox header="GID" fun={getSNL} />
        <SNLBox graph={graph ?? emptyG} setGeneList={setGraph} />
      </div>
      <GeneNetworkGraph graph={graph} />
    </div>
  );
}
