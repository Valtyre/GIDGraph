import React, { useEffect, useRef } from 'react';
import { DataSet, Edge, Network, Node } from 'vis-network/standalone';
import { Interaction } from './SNL/snlBox';
import { Infobox } from './infobox';

interface VisNode extends Node {
  id: string;
  label?: string;
}

interface VisEdge extends Edge {
  from: string;
  to: string;
  label?: string;
}

interface Graph {
  edges: Interaction[];
  node: string;
}

interface GeneNetworkGraphProps {
  graph: Graph | null;
  geneColors: Record<string, string>;
  isBusy?: boolean;
}

const GeneNetworkGraph: React.FC<GeneNetworkGraphProps> = ({
  graph,
  geneColors,
  isBusy = false,
}) => {
  const networkRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!networkRef.current || !graph || graph.edges.length === 0) return;

    const nodeIds = new Set<string>();
    graph.edges.forEach((edge) => {
      nodeIds.add(edge.from);
      nodeIds.add(edge.to);
    });

    const nodes: VisNode[] = Array.from(nodeIds).map((id) => ({
      id,
      label: id,
      shape: 'box',
      margin: { top: 12, right: 16, bottom: 12, left: 16 },
      color: {
        background: geneColors[id] ?? '#c9d0db',
        border: '#21303f',
        highlight: {
          background: geneColors[id] ?? '#c9d0db',
          border: '#174b5a',
        },
        hover: {
          background: geneColors[id] ?? '#c9d0db',
          border: '#174b5a',
        },
      },
      font: {
        color: '#1f2937',
        face: 'Manrope',
        size: 18,
        bold: {
          color: '#12202e',
          face: 'Manrope',
          size: 18,
          mod: 'bold',
        },
      },
      borderWidth: 1.5,
      borderWidthSelected: 2,
      shapeProperties: {
        borderRadius: 12,
      },
      shadow: {
        enabled: true,
        color: 'rgba(24, 35, 49, 0.18)',
        size: 18,
        x: 0,
        y: 10,
      },
    }));

    const edges: VisEdge[] = graph.edges.map((edge) => ({
      from: edge.from,
      to: edge.to,
      label: "",
      color: edge.label === "activation" ? "#2f7d60" : "#a44a4f",
      width: edge.label === "activation" ? 2.25 : 2.4,
      smooth: {
        enabled: true,
        type: 'dynamic',
        roundness: 0.2,
      },
      arrows: {
        to: {
          enabled: true,
          type: edge.label === "activation" ? "arrow" : "bar",
          scaleFactor: edge.label === "activation" ? 1.1 : 1.25,
        },
      },
      shadow: {
        enabled: true,
        color: 'rgba(25, 36, 54, 0.1)',
        size: 8,
        x: 0,
        y: 5,
      },
    }));

    const data = {
      nodes: new DataSet<VisNode>(nodes),
      edges: new DataSet<VisEdge>(edges),
    };

    const options = {
      autoResize: true,
      interaction: {
        hover: true,
        tooltipDelay: 150,
      },
      physics: {
        enabled: true,
        stabilization: {
          iterations: 180,
          updateInterval: 20,
        },
        barnesHut: {
          gravitationalConstant: -4200,
          centralGravity: 0.18,
          springLength: 170,
          springConstant: 0.04,
          damping: 0.16,
        },
      },
      layout: {
        improvedLayout: true,
      },
      nodes: {
        shape: 'box',
      },
      edges: {
        selectionWidth: 0,
        hoverWidth: 0,
      },
    };

    const network = new Network(networkRef.current, data, options);

    return () => {
      network.destroy();
    };
  }, [graph, geneColors]);

  const info = "Inspect the regulatory structure here.";

  const interactionCount = graph?.edges.length ?? 0;
  const geneCount = graph
    ? new Set(graph.edges.flatMap((edge) => [edge.from, edge.to])).size
    : 0;

  return (
    <section
      className="glass-panel workspace-panel animate-enter animate-delay-1 flex min-h-[640px] flex-col"
      role="region"
      aria-labelledby="graph-title"
    >
      <div className="panel-header">
        <div>
          <span className="eyebrow">Step 3</span>
          <div className="section-heading mt-4">
            <div>
              <h2 id="graph-title" className="panel-title">
                Regulatory network
              </h2>
              <p className="panel-subtitle">
                Interactive network view.
              </p>
            </div>
            <Infobox text={info} />
          </div>
        </div>

        <div className="hidden gap-3 lg:flex">
          <div className="status-pill">
            <span className="status-dot" />
            {geneCount} genes
          </div>
          <div className="status-pill">
            <span className="status-dot" />
            {interactionCount} interactions
          </div>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-[color:var(--color-ink-soft)]">
        <span className="inline-flex items-center gap-2 rounded-full border border-[color:var(--color-line)] bg-white/60 px-3 py-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--color-success)]" />
          Activation
        </span>
        <span className="inline-flex items-center gap-2 rounded-full border border-[color:var(--color-line)] bg-white/60 px-3 py-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--color-danger)]" />
          Inhibition
        </span>
        {isBusy && (
          <span className="inline-flex items-center gap-2 rounded-full border border-[color:rgba(31,95,114,0.14)] bg-[color:var(--color-accent-soft)] px-3 py-1.5 text-[color:var(--color-accent-strong)]">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Updating visualization
          </span>
        )}
      </div>

      <div className="relative flex-1 overflow-hidden rounded-[1.7rem] border border-[color:var(--color-line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.72)_0%,rgba(241,236,228,0.8)_100%)]">
        {graph && graph.edges.length > 0 ? (
          <div
            id="network"
            ref={networkRef}
            className="h-[620px] w-full"
            role="img"
            aria-label="Gene regulatory network visualization"
          />
        ) : (
          <div className="empty-state m-4 h-[calc(100%-2rem)]">
            <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[color:var(--color-line)] bg-white/85 shadow-[0_14px_30px_rgba(28,40,58,0.1)]">
              <svg className="h-7 w-7 text-[color:var(--color-accent-strong)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M8 12h8m-4-4v8m9-4a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-lg font-semibold text-foreground">Your network will appear here.</p>
            <p className="max-w-md text-sm">
              Parse text above or add interactions manually.
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default GeneNetworkGraph;
