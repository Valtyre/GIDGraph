'use client'

import GeneInteractionBubble from "./geneInteractionBubble";
import { useEffect, useRef, useState } from "react";

export enum InteractionType {
    activation, 
    inhibition
}

export type Interaction = {
  from: string,
  to: string, 
  label: InteractionType, 
  id: number
}



export function SNLBox({geneInteractions}: {geneInteractions: Interaction[]}) {
  
  const [SemiNaturalLanguage, setSemiNaturalLanguage] = useState<Interaction[]>([])

  const uniqueID = useRef(0);


  useEffect( () => {
    geneInteractions.forEach(element => {createInteraction(element)
    }); 
  }, [geneInteractions])

  console.log("SEMI:", SemiNaturalLanguage)

  const interactionTemplate = {from: "", label: InteractionType.activation, to: ""}


  function flipInteraction(interaction: Interaction): void {
    const snl = [...SemiNaturalLanguage];
    const index = snl.findIndex((i) => i.id === interaction.id);

    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        from: current.to,
        to: current.from,
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
        label: interaction.label == InteractionType.activation ? InteractionType.inhibition : InteractionType.activation,
      };
      setSemiNaturalLanguage(snl);
    }
    console.log(SemiNaturalLanguage)
  }


  function createInteraction(i: { from: string; label: InteractionType; to: string }) {
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
