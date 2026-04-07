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
        flex w-full max-w-[700px] mx-auto items-center gap-2 
        p-2 
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
          w-6 h-6 
          text-xl font-bold 
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
          text-center text-sm
          bg-main text-foreground 
          px-2 py-1.5 
          rounded-md
          border-3
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-offset-1
        "
        style={{ 
          borderColor: fromColor,
          borderWidth: '3px'
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
          px-3 py-1.5 min-w-[85px]
          text-xs font-semibold text-white
          rounded-md
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
          text-center text-sm
          bg-main text-foreground 
          px-2 py-1.5 
          rounded-md
          border-3
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-offset-1
        "
        style={{ 
          borderColor: toColor,
          borderWidth: '3px'
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
