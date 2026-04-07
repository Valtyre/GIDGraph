import { Interaction } from './snlBox';
import { useState } from 'react';

type GeneInteractionProps = {
  interaction: Interaction;
  geneColors: Record<string,string>;
  onFlip: () => void;
  onToggleType: () => void;
  onRemove: () => void;
  changeFrom: (i: Interaction, s: string) => void; 
  changeTo: (i: Interaction, s: string) => void;
};

export default function GeneInteractionBubble({ interaction, geneColors, onToggleType, onRemove, changeFrom, changeTo}: GeneInteractionProps) {
  
  const fromColor = geneColors[interaction.from] ?? "#9ca3af"
  const toColor = geneColors[interaction.to] ?? "#9ca3af" 

  const [textFrom, setTextFrom] = useState(interaction.from);
  const [textTo, setTextTo] = useState(interaction.to);
  
  const { from, label, to } = interaction;

  const isActivation = label === "activation";

  return (
    <div 
      className="
        flex w-full max-w-[800px] mx-auto items-center gap-3 
        p-3 
        bg-second rounded-lg 
        shadow-sm
        transition-shadow duration-200
        hover:shadow-md
      " 
      role="listitem"
      tabIndex={0}
    >
      {/* Delete button */}
      <button
        className="
          flex items-center justify-center
          w-8 h-8 
          text-2xl font-bold 
          text-third/70
          rounded-full
          transition-all duration-150
          hover:bg-third/10 hover:text-third
          focus:bg-third/10 focus:text-third
        "
        onClick={onRemove}
        aria-label="Delete interaction"
        title="Delete interaction"
      >
        ×
      </button>

      {/* From gene input */}
      <input 
        type="text"
        className="
          flex-1 min-w-0
          text-center text-base
          bg-main text-foreground 
          px-3 py-2 
          rounded-lg
          border-4
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-offset-1
        "
        style={{ 
          borderColor: fromColor,
          boxShadow: `0 0 0 0 ${fromColor}` 
        }}    
        value={textFrom}
        onChange={(e) => {
          const value = e.target.value;
          changeFrom(interaction, value);
          setTextFrom(value);
        }}
        placeholder="Gene..."
        aria-label="Source gene"
      />

      {/* Interaction type toggle */}
      <button
        className={`
          px-4 py-2 min-w-[100px]
          text-sm font-semibold text-white
          rounded-lg
          transition-all duration-150
          ${isActivation 
            ? 'btn-activation' 
            : 'btn-inhibition'
          }
        `}
        onClick={onToggleType}
        aria-label={`Toggle interaction type, currently ${label}`}
        title="Click to toggle between activation and inhibition"
      >
        {isActivation ? 'activates' : 'inhibits'}
      </button>

      {/* To gene input */}
      <input 
        type="text"
        className="
          flex-1 min-w-0
          text-center text-base
          bg-main text-foreground 
          px-3 py-2 
          rounded-lg
          border-4
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-offset-1
        "
        style={{ 
          borderColor: toColor,
          boxShadow: `0 0 0 0 ${toColor}` 
        }}    
        value={textTo}
        onChange={(e) => {
          const value = e.target.value;
          changeTo(interaction, value);
          setTextTo(value);
        }}
        placeholder="Gene..."
        aria-label="Target gene"
      />
    </div>
  );
}
