'use client'

import { Graph } from "@/app/page";
import GeneInteractionBubble from "./geneInteractionBubble";
import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { AddButton } from "./addButton";
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



export function SNLBox({graph, setGeneList, geneColors}: {graph: Graph, setGeneList: Dispatch<SetStateAction<Graph | null>>, geneColors: Record<string,string>}) {
  
  
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
  
  function changeF(interaction: Interaction, s: string): void {
    console.log("changef")
    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);
      
    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        from: s,
      };
      console.log("ree: ")
      setGeneList({edges: snl, node: nodes});
    }
  }
  function changeT(interaction: Interaction, s: string): void {

    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);
      
    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        to: s,
      };

      setGeneList({edges: snl, node: nodes});
    }
  }


  return (
    <div className="flex flex-col mx-auto w-full p-5">
      <h1 className="font-bold text-3xl text-second">Semi-Natural Language</h1>
      <div className="flex flex-col p-3 gap-2 overflow-scroll bg-off border-2 border-third rounded-sm">
        {geneList ? geneList.map((inter, index) => (
          <GeneInteractionBubble key={index}
          interaction={inter}
          geneColors={geneColors}
          onFlip={() => flipInteraction(inter)}
          onToggleType={() => toggleType(inter)}
          onRemove={() => removeInteraction(inter)}
          changeFrom={changeF}
          changeTo={changeT}
          />
        )) : []}
        <AddButton add={addInteraction}/>

      </div>
    </div>
  );
}
