/* ─────────────────────────────────────────────────────────── page.tsx ── */
/*  Main “Home” route for the front‑end:                                     
      1. calls FastAPI /parse → receives a Graph                            
      2. derives logical formulas + pastel colours                          
      3. renders input boxes  |  network graph  |  formula bubbles          */
/*  NOTE:  every edge coming from the backend is given a unique `id` here   */
/* ───────────────────────────────────────────────────────────────────────── */

'use client';

import { useState, useEffect } from 'react';

/* ── local components ─────────────────────────────────────────────────── */
import TopBar from './Elements/TopBar';
import NatrualLanguageBox from './Elements/natrualLanguageBox';
import { SNLBox, Interaction } from './Elements/SNL/snlBox';
import GeneNetworkGraph from './Elements/graph';
import LogicalFormulasContainer, {
  LogicalFormula as LF,
} from './Elements/logicalFormulas/lfContainer';

/* ── helpers ──────────────────────────────────────────────────────────── */
import { buildLogicalFormulas } from './Elements/logicalFormulas/lfBuilder';

/* ── Type definitions ─────────────────────────────────────────────────── */
export type Graph = {
  node: string;          // (unused for now)
  edges: Interaction[];
};

/* ── pastel palette: golden‑angle sequence for distinct colours ───────── */
const pastel = (idx: number) =>
  `hsl(${(idx * 137.508) % 360} 70% 65%)`;   // pleasant pastels

/* ─────────────────────────────────────────────────────────────────────── */
export default function Home() {
  /* graph from the backend (or null before first fetch) */
  const [graph, setGraph] = useState<Graph | null>(null);

  /* logical‑formulas derived from `graph` */
  const [lf, setLF] = useState<LF[]>([]);

  /* gene → colour map shared by graph nodes & LF bubbles */
  const [geneColors, setGeneColors] = useState<Record<string, string>>({});

  /* ───────────── API call & unique‑id injection ───────────── */
  
  

  /* ─── rebuild formulas & colours whenever `graph` changes ── */
  useEffect(() => {
    setLF(buildLogicalFormulas(graph));

    if (graph) {
      /* collect distinct gene names */
      const genes = new Set<string>();
      graph.edges.forEach(e => {
        genes.add(e.from);
        genes.add(e.to);
      });

      /* assign each gene a pastel colour once */
      const cmap: Record<string, string> = {};
      [...genes].forEach((g, i) => (cmap[g] = pastel(i)));
      setGeneColors(cmap);
    }
  }, [graph]);

  /* fallback graph for SNLBox before fetch completes */
  const emptyGraph: Graph = { node: '', edges: [] };

  /* ────────────────────────── JSX ─────────────────────────── */
  return (
    <div className="min-h-screen bg-main ">
      {/* header bar */}
      <TopBar />

      {/* input area: natural language + SNL editor */}
      <div className="flex flex-row h-[400px]">
        <NatrualLanguageBox fun={setGraph} graph={graph} />
        <SNLBox 
          graph={graph ?? emptyGraph} 
          setGeneList={setGraph}
          geneColors={geneColors}
        />
      </div>

      {/* main content: graph (65 %)  |  logical formulas (35 %) */}
      <div className="flex flex-row">
        <div className="flex-[2]">
          <GeneNetworkGraph graph={graph} geneColors={geneColors} />
        </div>

        <div className="flex-[1] overflow-y-auto max-h-[600px] p-4">
          <LogicalFormulasContainer
            lf={lf}
            setLF={setLF}
            geneColors={geneColors}
          />
        </div>
      </div>
    </div>
  );
}
/* ─────────────────────────────────────────────────────────────────────── */
