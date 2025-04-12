'use client'

import { Graph } from "@/app/page";
import GeneInteractionBubble from "./geneInteractionBubble";
import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";

export enum InteractionType {
  activation = "activation",
  inhibition = "inhibition"
}


export type Interaction = {
  from: string,
  to: string, 
  label: InteractionType, 
  id: number
}



export function SNLBox({graph, setGeneList}: {graph: Graph, setGeneList: Dispatch<SetStateAction<Graph | null>>}) {
  
  
  const [geneList, nodes] = [graph.edges , graph.node]

  const uniqueID = useRef(0);


  const interactionTemplate = {from: "", label: InteractionType.activation, to: ""}


  function flipInteraction(interaction: Interaction): void {
    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);

    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        from: current.to,
        to: current.from,
      };
      setGeneList({edges: snl, node: nodes});
    }
    console.log(geneList)
  }

  function toggleType(interaction: Interaction): void {
    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);
      
    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        label: interaction.label == InteractionType.activation ? InteractionType.inhibition : InteractionType.activation,
      };
      setGeneList({edges: snl, node: nodes});
    }
    console.log(geneList)
  }


  function createInteraction(i: { from: string; label: InteractionType; to: string }) {
    setGeneList(prev => ({
      node: nodes,
      edges: prev ? [
        ...prev.edges,
        {
          id: uniqueID.current++,
          ...i,
        },
      ] : [],
    })); 
  }
  
  


  function addInteraction(){
      createInteraction(interactionTemplate)
  }

  function removeInteraction(i: Interaction): void {
      setGeneList({edges: geneList.filter((int) => int.id !== i.id), node: nodes})
    }
    


  return (
    <div className="flex flex-col w-full p-5">
      <h1 className="font-bold text-3xl text-white">Semi-Natural Language</h1>
      <div className="flex flex-col p-5 gap-5 overflow-scroll bg-blue-900 border border-white rounded-md">
      {geneList ? geneList.map((inter, index) => (
          <GeneInteractionBubble key={index}
          interaction={inter}
          onFlip={() => flipInteraction(inter)}
          onToggleType={() => toggleType(inter)}
          onRemove={() => removeInteraction(inter)}
        />
        )) : []}
      

      </div>
    </div>
  );
}
