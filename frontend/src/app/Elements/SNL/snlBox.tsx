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

export function SNLBox({ graph, setGeneList, geneColors }: SNLBoxProps) {
  const [geneList, nodes] = [graph.edges, graph.node];
  const uniqueID = useRef(geneList.length + 1);

  function toggleType(interaction: Interaction): void {
    const snl = [...geneList];
    const index = snl.findIndex((i) => i.id === interaction.id);

    if (index !== -1) {
      const current = snl[index];
      snl[index] = {
        ...current,
        label:
          interaction.label == InteractionType.activation
            ? InteractionType.inhibition
            : InteractionType.activation,
      };
      setGeneList({ edges: snl, node: nodes });
    }
  }

  function createInteraction(i: { from: string; label: InteractionType; to: string, id: number }) {
    setGeneList((prev) => ({
      node: nodes,
      edges: prev
        ? [
            ...prev.edges,
            {
              ...i,
            },
          ]
        : [],
    }));
  }

  function addInteraction() {
    const newInteraction = {
      from: "",
      label: InteractionType.activation,
      to: "",
      id: uniqueID.current++,
    };
    createInteraction(newInteraction);
  }

  function removeInteraction(i: Interaction): void {
    setGeneList({ edges: geneList.filter((int) => int.id !== i.id), node: nodes })
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
      setGeneList({ edges: snl, node: nodes });
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
      setGeneList({ edges: snl, node: nodes });
    }
  }

  const info = "Refine the extracted interactions here.";

  return (
    <section
      className="glass-panel workspace-panel animate-enter animate-delay-1 flex h-[560px] flex-col"
      role="region"
      aria-labelledby="snl-title"
    >
      <div className="panel-header">
        <div>
          <span className="eyebrow">Step 2</span>
          <div className="section-heading mt-4">
            <div>
              <h2 id="snl-title" className="panel-title">
                Structured interactions
              </h2>
              <p className="panel-subtitle">
                Edit the parsed interactions.
              </p>
            </div>
            <Infobox text={info} />
          </div>
        </div>

        <div className="hidden rounded-[1.2rem] border border-[color:var(--color-line)] bg-white/55 px-4 py-3 text-right lg:block">
          <p className="text-[0.72rem] font-extrabold uppercase tracking-[0.16em] text-[color:var(--color-accent-strong)]">
            Rows
          </p>
          <p className="mt-1 text-sm text-[color:var(--color-ink-soft)]">
            {geneList.length} interaction{geneList.length === 1 ? "" : "s"}
          </p>
        </div>
      </div>

      <div
        className="custom-scrollbar flex h-full flex-1 flex-col gap-3 overflow-y-auto rounded-[1.5rem] border border-[color:var(--color-line)] bg-[rgba(255,253,249,0.68)] p-4"
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
              onToggleType={() => toggleType(inter)}
              onRemove={() => removeInteraction(inter)}
              changeFrom={changeF}
              changeTo={changeT}
            />
          ))
        ) : (
          <div className="empty-state">
            <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[color:var(--color-line)] bg-white/80">
              <svg className="h-6 w-6 text-[color:var(--color-accent-strong)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.7} d="M12 5v14m7-7H5" />
              </svg>
            </div>
            <p className="text-base font-semibold text-foreground">No structured interactions yet.</p>
            <p className="max-w-sm text-sm">
              Parse text above or add rows manually.
            </p>
          </div>
        )}

        <AddButton add={addInteraction} />
      </div>
    </section>
  );
}
