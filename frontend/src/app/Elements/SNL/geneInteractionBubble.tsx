import { Interaction } from './snlBox';
import { useEffect, useState } from 'react';

type GeneInteractionProps = {
  interaction: Interaction;
  geneColors: Record<string, string>;
  onToggleType: () => void;
  onRemove: () => void;
  changeFrom: (i: Interaction, s: string) => void;
  changeTo: (i: Interaction, s: string) => void;
};

export default function GeneInteractionBubble({
  interaction,
  geneColors,
  onToggleType,
  onRemove,
  changeFrom,
  changeTo,
}: GeneInteractionProps) {
  const fromColor = geneColors[interaction.from] ?? "#b9c0cb";
  const toColor = geneColors[interaction.to] ?? "#b9c0cb";
  const [textFrom, setTextFrom] = useState(interaction.from);
  const [textTo, setTextTo] = useState(interaction.to);
  const { label } = interaction;
  const isActivation = label === "activation";

  useEffect(() => {
    setTextFrom(interaction.from);
    setTextTo(interaction.to);
  }, [interaction.from, interaction.to]);

  return (
    <div
      className="rounded-[1.35rem] border border-[color:var(--color-line)] bg-[rgba(255,255,255,0.82)] p-3 shadow-[0_12px_30px_rgba(27,38,54,0.08)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_18px_40px_rgba(27,38,54,0.12)]"
      role="listitem"
      tabIndex={0}
    >
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center">
        <div className="flex flex-1 flex-col gap-3 md:flex-row md:items-center">
          <div className="min-w-0 flex-1">
            <p className="mb-2 text-[0.72rem] font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-ink-soft)]">
              Source gene
            </p>
            <input
              type="text"
              className="workspace-input h-12 px-4 text-sm font-semibold"
              style={{
                borderColor: fromColor,
                boxShadow: `inset 0 1px 0 rgba(255,255,255,0.8), 0 0 0 1px ${fromColor}30`,
              }}
              value={textFrom}
              onChange={(e) => {
                const value = e.target.value;
                changeFrom(interaction, value);
                setTextFrom(value);
              }}
              placeholder="Gene name"
              aria-label="Source gene"
            />
          </div>

          <div className="flex shrink-0 flex-col items-center justify-center gap-2">
            <p className="text-[0.72rem] font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-ink-soft)]">
              Relation
            </p>
            <button
              className={`btn min-w-[150px] ${isActivation ? 'btn-activation' : 'btn-inhibition'}`}
              onClick={onToggleType}
              aria-label={`Toggle interaction type, currently ${label}`}
              title="Click to toggle between activation and inhibition"
            >
              {isActivation ? 'Activates' : 'Inhibits'}
            </button>
          </div>

          <div className="min-w-0 flex-1">
            <p className="mb-2 text-[0.72rem] font-extrabold uppercase tracking-[0.14em] text-[color:var(--color-ink-soft)]">
              Target gene
            </p>
            <input
              type="text"
              className="workspace-input h-12 px-4 text-sm font-semibold"
              style={{
                borderColor: toColor,
                boxShadow: `inset 0 1px 0 rgba(255,255,255,0.8), 0 0 0 1px ${toColor}30`,
              }}
              value={textTo}
              onChange={(e) => {
                const value = e.target.value;
                changeTo(interaction, value);
                setTextTo(value);
              }}
              placeholder="Gene name"
              aria-label="Target gene"
            />
          </div>
        </div>

        <button
          className="inline-flex h-11 w-11 shrink-0 items-center justify-center self-end rounded-full border border-[color:var(--color-line)] bg-white/90 text-lg font-bold text-[color:var(--color-ink-soft)] transition-all duration-150 hover:border-[color:rgba(164,74,79,0.3)] hover:bg-[color:var(--color-danger-soft)] hover:text-[color:var(--color-danger)] xl:self-center"
          onClick={onRemove}
          aria-label="Delete interaction"
          title="Delete interaction"
        >
          ×
        </button>
      </div>
    </div>
  );
}
