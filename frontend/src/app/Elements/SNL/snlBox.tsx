'use client'

import { Graph } from "@/app/page";
import GeneInteractionBubble from "./geneInteractionBubble";
import { Dispatch, SetStateAction, useRef } from "react";
import { AddButton } from "./addButton";
import { Infobox } from "../infobox";

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

type SNLBoxProps = {
  graph: Graph,
  setGeneList: Dispatch<SetStateAction<Graph | null>>,
  geneColors: Record<string, string>
}

export function SNLBox({graph, setGeneList, geneColors}: SNLBoxProps) {
  
  const [geneList, nodes] = [graph.edges , graph.node]
  const uniqueID = useRef(geneList.length+1);

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
  }

  function createInteraction(i: { from: string; label: InteractionType; to: string, id: number }) {
    setGeneList(prev => ({
      node: nodes,
      edges: prev ? [
        ...prev.edges,
        {
          ...i,
        },
      ] : [],
    })); 
  }

  function addInteraction(){
    const newInteraction = {
      from: "", 
      label: InteractionType.activation, 
      to: "", 
      id: uniqueID.current++
    };
    createInteraction(newInteraction);
  }

  function removeInteraction(i: Interaction): void {
      setGeneList({edges: geneList.filter((int) => int.id !== i.id), node: nodes})
    }
  
  function changeF(interaction: Interaction, s: string): void {
    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);
      
    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        from: s,
      };
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

  const info = `
  In this field you can add, remove and edit gene interactions. You can do this by clicking on the different elements. 
  These changes will be reflected in the visualisation, but changing elements here will not impact the natural language discriptions.
  `

  return (
    <section 
      className="flex flex-col w-full h-full p-5 lg:p-6 overflow-hidden"
      role="region"
      aria-labelledby="snl-title"
    >
      <h2 id="snl-title" className="section-heading text-2xl lg:text-3xl flex-shrink-0">
        Semi-Natural Language
        <Infobox text={info}/>
      </h2>

      <div 
        className="
          flex flex-col gap-3 p-4
          flex-1 min-h-0 overflow-y-auto
          bg-off border-2 border-third/30 
          rounded-lg
          custom-scrollbar
          transition-colors duration-200
          hover:border-third/50
        "
        tabIndex={0}
        role="list"
        aria-label="Gene interactions list"
      >
        {geneList && geneList.length > 0 ? (
          geneList.map((inter) => (
            <GeneInteractionBubble 
              key={inter.id}
              interaction={inter}
              geneColors={geneColors}
              onFlip={() => flipInteraction(inter)}
              onToggleType={() => toggleType(inter)}
              onRemove={() => removeInteraction(inter)}
              changeFrom={changeF}
              changeTo={changeT}
            />
          ))
        ) : (
          <p className="text-center text-gray-500 py-8">
            No interactions yet. Add one below or convert text above.
          </p>
        )}
        
        <AddButton add={addInteraction}/>
      </div>
    </section>
  );
}
