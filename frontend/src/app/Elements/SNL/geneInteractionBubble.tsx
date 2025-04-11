import { useSignal } from '@preact/signals-react';
import { Interaction, InteractionType } from './snlBox';

type Props = {
  interaction: Interaction;
  onFlip: () => void;
  onToggleType: () => void;
  onRemove: () => void;
};

export default function GeneInteractionBubble({ interaction, onFlip, onToggleType, onRemove }: Props) {
  
  console.log(interaction)
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

      <span className="text-center flex-1 text-2xl">{from}</span>

      <div className="flex flex-col items-center gap-2">
        <button
          className={`border-gray-400 rounded-md px-3 py-1 min-w-25 ${buttonColor}`}
          onClick={onToggleType}
        >
          {label == "activation" ? 'activates' : 'inhibits'}
        </button>

        <button
          className="bg-white border border-gray-400 rounded-md px-3 py-1 hover:bg-gray-100 min-w-25"
          onClick={onFlip}
        >
          &#8596;
        </button>
      </div>

      <span className="text-center flex-1 text-2xl">{to}</span>
    </div>
  );
}
