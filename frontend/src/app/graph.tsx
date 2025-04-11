import React, { useEffect, useRef } from 'react';
import { DataSet, Network, Node, Edge } from 'vis-network/standalone';
import { Interaction, InteractionType } from './Elements/SNL/snlBox'; // Adjust the path if needed

interface VisNode extends Node {
  id: string;
  label?: string;
}

interface VisEdge extends Edge {
  from: string;
  to: string;
  label?: string;
  color?: string;
  arrows?: string;
}

interface Graph {
  edges: Interaction[];
  node: string;
}

interface GeneNetworkGraphProps {
  graph: Graph | null;
}

const GeneNetworkGraph: React.FC<GeneNetworkGraphProps> = ({ graph }) => {
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
    }));

    const edges: VisEdge[] = graph.edges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: edge.label,
      color: edge.label == "activation" ? "green" : "red",
      arrows: edge.label == "activation" ? "to" : "",
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
          borderRadius: 5,
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
  }, [graph]);

  return (
    <div className="p-5 bg-midnight">
      <div
        id="network"
        className="w-9/10 max-w-[800px] h-[600px] m-auto bg-graph shadow-[0_4px_8px_rgba(0,0,0,0.4)]"
        ref={networkRef}
      />
    </div>
  );
};

export default GeneNetworkGraph;
