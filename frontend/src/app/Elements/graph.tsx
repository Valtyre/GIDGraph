import React, { useEffect, useRef } from 'react';
import { DataSet, Network, Node, Edge } from 'vis-network/standalone';
import { Interaction, InteractionType } from './SNL/snlBox'; // Adjust the path if needed

interface VisNode extends Node {
  id: string;
  label?: string;
}

interface VisEdge extends Edge {
  from: string;
  to: string;
  label?: string;
  color?: string;
  arrows?: string | {
    to?: {
      enabled: boolean;
      type?: 'arrow' | 'bar' | 'circle' | 'image';
      scaleFactor?: number;
    };
    from?: {
      enabled: boolean;
      type?: 'arrow' | 'bar' | 'circle' | 'image';
      scaleFactor?: number;
    };
    middle?: {
      enabled: boolean;
      type?: 'arrow' | 'bar' | 'circle' | 'image';
      scaleFactor?: number;
    };
  };
}


interface Graph {
  edges: Interaction[];
  node: string;
}

interface GeneNetworkGraphProps {
  graph: Graph | null;
  geneColors: Record<string, string>;
}

const GeneNetworkGraph: React.FC<GeneNetworkGraphProps> = ({ graph, geneColors }) => {
  const networkRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!networkRef.current || !graph) return;

    // Build unique set of nodes from edges
    const nodeIds = new Set<string>();
    graph.edges.forEach(edge => {
      nodeIds.add(edge.from);
      nodeIds.add(edge.to);
    });

    const nodes: VisNode[] = Array.from(nodeIds).map(id => ({
      id,
      label: id,
      /* pastel background, dark border */
      color: {
        background: geneColors[id] ?? '#6b7280',
        border: '#1f2937',
        highlight: { background: geneColors[id] ?? '#6b7280' },
      },
    }));

    const edges: VisEdge[] = graph.edges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: edge.label,
      color: edge.label === "activation" ? "green" : "red",
      arrows: {
        to: {
          enabled: true,
          type: edge.label === "activation" ? "arrow" : "bar",
          scaleFactor: 1,
        },
      },
    }));
    

    const visNodes = new DataSet<VisNode>(nodes);
    const visEdges = new DataSet<VisEdge>(edges);

    const data = { nodes: visNodes, edges: visEdges };

    const options = {
      physics: {
        enabled: true,
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 95,
        },
      },
      nodes: {
        shape: 'box',
        shapeProperties: {
          borderRadius: 7,
        },
        font: {
          color: '#ffffff',
          size: 16,
          face: 'Arial',
          vadjust: 1.5,
        },
      },
      edges: {
        font: { size: 0 },
      },
    };

    new Network(networkRef.current, data, options);
  }, [graph, geneColors]);

  return (
    <div className="p-5 h-full w-full flex-1">
      <div
        id="network"
        ref={networkRef}
        className="w-full h-[600px] bg-second shadow-[0_4px_8px_rgba(0,0,0,0.4)]"
      />
    </div>
  );
};

export default GeneNetworkGraph;
