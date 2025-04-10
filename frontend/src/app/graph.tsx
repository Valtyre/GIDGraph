import React, { useEffect, useRef } from 'react';
import { DataSet, Network, Node, Edge } from 'vis-network/standalone';

interface GeneNetworkGraphProps {
  fileName: string; // The path to the JSON graph file
}

// Extend Node and Edge types if needed, or define them to match your JSON structure.
interface VisNode extends Node {
  id: number | string; // Ensure id is non-nll (adjust the type if your ids are numbers or strings)
  label?: string;

}

interface VisEdge extends Edge {
  id?: number | string;
  from: number | string;
  to: number | string;
  // Add additional edge properties if needed
}

const GeneNetworkGraph: React.FC<GeneNetworkGraphProps> = ({ fileName }) => {
  const networkRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (networkRef.current) {
      fetch(fileName)
        .then((response) => response.json())
        .then((data) => {
          // Explicitly type the nodes and edges from your JSON data.
          const nodes = new DataSet<VisNode>(data.nodes);
          const edges = new DataSet<VisEdge>(data.edges);

          const graphData = { nodes, edges };

          // Define network options
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
                borderRadius: 5, // Rounded corners
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

          // Create a network instance in the designated container.
          if (networkRef.current != null) {new Network(networkRef.current, graphData, options);}
        })
        .catch((error) => console.error('Error loading JSON file:', error));
    }
  }, [fileName]);

  return (
    <div className="p-5 bg-midnight">
      <div id="network" className='w-9/10 max-w-[800px] h-[600px] m-auto bg-graph shadow-[0_4px_8px_rgba(0,0,0,0.4)]' ref={networkRef} />
    </div>
  );
};

export default GeneNetworkGraph;
