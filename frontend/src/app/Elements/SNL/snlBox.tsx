'use client'
import { useComputed } from "@preact/signals-react";
import GeneInteractionBubble from "./geneInteractionBubble";
import { useEffect, useRef, useState } from "react";

export enum InteractionType {
    activation, 
    inhibition
}

export type Interaction = {
    source: string, 
    type: InteractionType, 
    target: string,
    id: number
}

const geneInteractions = [
  { source: "gene1", target: "gene5", type: InteractionType.activation },
  { source: "gene2", target: "gene6", type: InteractionType.inhibition },
  { source: "gene3", target: "gene7", type: InteractionType.activation },
  { source: "gene4", target: "gene8", type: InteractionType.activation },
];



export function SNLBox() {
  
  const [SemiNaturalLanguage, setSemiNaturalLanguage] = useState<Interaction[]>([])

  const uniqueID = useRef(0);


  useEffect( () => {
    geneInteractions.forEach(element => {createInteraction(element)
    }); 
  }, [])
  

const interactionTemplate = {source: "", type: InteractionType.activation, target: ""}


function flipInteraction(interaction: Interaction): void {
  const snl = [...SemiNaturalLanguage];
  const index = snl.findIndex((i) => i.id === interaction.id);

  if (index !== -1) {
    const current = snl[index];
    snl[index] = {
      ...current,
      source: current.target,
      target: current.source,
    };
    setSemiNaturalLanguage(snl);
  }
  console.log(SemiNaturalLanguage)
}

function toggleType(interaction: Interaction): void {
  const snl = [...SemiNaturalLanguage];
  const index = snl.findIndex((i) => i.id === interaction.id);
    
  if (index !== -1) {
    const current = snl[index];
    snl[index] = {
      ...current,
      type: interaction.type == InteractionType.activation ? InteractionType.inhibition : InteractionType.activation,
    };
    setSemiNaturalLanguage(snl);
  }
  console.log(SemiNaturalLanguage)
}


function createInteraction(i: { source: string; type: InteractionType; target: string }) {
  setSemiNaturalLanguage(prev => [
    ...prev,
    {
      id: uniqueID.current++,
      ...i,
    },
  ]);
}


function addInteraction(){
    createInteraction(interactionTemplate)
}

function removeInteraction(i: Interaction): void {
    setSemiNaturalLanguage(SemiNaturalLanguage.filter((int) => int.id !== i.id))
  }
  


  return (
    <div className="flex flex-col w-full p-5">
      <h1 className="font-bold text-3xl text-white">Semi-Natural Language</h1>
      <div className="flex flex-col p-5 gap-5 overflow-scroll bg-blue-900 border border-white rounded-md">
      {SemiNaturalLanguage.map((inter, index) => (
          <GeneInteractionBubble key={index}
          interaction={inter}
          onFlip={() => flipInteraction(inter)}
          onToggleType={() => toggleType(inter)}
          onRemove={() => removeInteraction(inter)}
        />
        ))}
      

      </div>
    </div>
  );
}
