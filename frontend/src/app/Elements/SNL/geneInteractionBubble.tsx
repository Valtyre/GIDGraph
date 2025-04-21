import { useSignal } from '@preact/signals-react';
import { Interaction, InteractionType } from './snlBox';
import { useState } from 'react';

type Props = {
  interaction: Interaction;
  geneColors: Record<string,string>;
  onFlip: () => void;
  onToggleType: () => void;
  onRemove: () => void;
  changeFrom: (i: Interaction, s: string) => void; 
  changeTo: (i: Interaction, s: string) => void;
};

export default function GeneInteractionBubble({ interaction, geneColors, onToggleType, onRemove, changeFrom, changeTo}: Props) {
  
  const fromColor = geneColors[interaction.from] ?? "#9ca3af"
  const toColor = geneColors[interaction.to] ?? "#9ca3af" 

  const [textFrom, setTextFrom] = useState(interaction.from);
  const [textTo, setTextTo] = useState(interaction.to);
  
  // console.log(interaction)
  const { from, label, to } = interaction;


  const buttonColor =
    label == "activation"
      ? 'bg-green-500 hover:bg-green-600'
      : 'bg-red-500 hover:bg-red-600';

  return (
    <div className="relative flex items-center justify-center mx-auto w-full p-5 gap-5 bg-blue-200 rounded-md">
      <button
        className="absolute top-2 right-2 text-gray-600 hover:text-red-600 text-sm font-bold"
        onClick={onRemove}
        aria-label="Delete"
      >
        ×
      </button>

      <input type="text"
        className= "text-center bg-white flex-1 text-2xl text-black"
        style={{ border: `5px solid ${fromColor}` }}    
        value={textFrom}
        onChange={(e) => {
          console.log(e.target.value)
          const value = e.target.value;
          changeFrom(interaction, value);
          setTextFrom(value);
        }}
      />


      <div className="flex flex-col items-center gap-2">
        <button
          className={`border-gray-400 rounded-md px-3 py-1 min-w-25 ${buttonColor}`}
          onClick={onToggleType}
        >
          {label == "activation" ? 'activates' : 'inhibits'}
        </button>

        {/* <button
          className="bg-white border border-gray-400 rounded-md px-3 py-1 hover:bg-gray-100 min-w-25"
          onClick={onFlip}
        >
          &#8596;
        </button> */}
      </div>

      <input type="text"
        className= "text-center bg-white flex-1 text-2xl text-black"
        style={{ border: `5px solid ${toColor}` }}    
        value={textTo}
        onChange={(e) => {
          console.log(e.target.value)
          const value = e.target.value;
          changeTo(interaction, value);
          setTextTo(value);
        }}
      />
    </div>
  );
}
