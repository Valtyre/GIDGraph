import { Graph } from "../../page";
import { LogicalFormula as LF } from "./lfContainer";
import { Interaction } from "../SNL/snlBox";

/**
 * Convert Graph -> array of logical‑formula objects.
 * Rule set:
 *   • Each Interaction becomes an entry under its targetGene.
 *   • label = true  => activation
 *   • label = false => inhibition
 *   • truthValue default = false   (checkbox unchecked)
 */
export function buildLogicalFormulas(graph: Graph | null): LF[] {
  if (!graph) return [];

  // Map targetGene -> incomingGenes[]
  const map = new Map<string, LF["incomingGenes"]>();

  graph.edges.forEach((edge: Interaction) => {
    const entry = map.get(edge.to) ?? [];

    entry.push({
      gene: edge.from,
      label: edge.label === "activation", // true for activation
      truthValue: true                   // default = is set to AND
    });

    map.set(edge.to, entry);
  });

  // Convert map -> LF[]
  const lfArray: LF[] = [];
  map.forEach((incomingGenes, targetGene) => {
    lfArray.push({ targetGene, incomingGenes });
  });

  return lfArray;
}
