'use client';

import { useEffect, useState } from 'react';
import TopBar from './Elements/TopBar';
import NatrualLanguageBox from './Elements/natrualLanguageBox';
import { SNLBox, Interaction } from './Elements/SNL/snlBox';
import GeneNetworkGraph from './Elements/graph';
import LogicalFormulasContainer, {
  LogicalFormula as LF,
} from './Elements/logicalFormulas/lfContainer';
import { buildApiUrl } from '../lib/apiConfig';
import { buildLogicalFormulas } from './Elements/logicalFormulas/lfBuilder';

export type Graph = {
  node: string;
  edges: Interaction[];
};

const pastel = (idx: number) =>
  `hsl(${(idx * 137.508) % 360} 58% 73%)`;

export default function Home() {
  const [graph, setGraph] = useState<Graph | null>(null);
  const [lf, setLF] = useState<LF[]>([]);
  const [geneColors, setGeneColors] = useState<Record<string, string>>({});
  const [isExporting, setIsExporting] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);

  function exportGinml() {
    if (!graph || isExporting) return;

    setIsExporting(true);
    fetch(buildApiUrl("/api/export_ginml"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ graph, lf }),
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "model.ginml";
        a.click();
        URL.revokeObjectURL(url);
      })
      .catch(console.error)
      .finally(() => setIsExporting(false));
  }

  useEffect(() => {
    setLF(buildLogicalFormulas(graph));

    if (graph) {
      const genes = new Set<string>();
      graph.edges.forEach((e) => {
        genes.add(e.from);
        genes.add(e.to);
      });

      const cmap: Record<string, string> = {};
      [...genes].forEach((g, i) => (cmap[g] = pastel(i)));
      setGeneColors(cmap);
    } else {
      setGeneColors({});
    }
  }, [graph]);

  const emptyGraph: Graph = { node: '', edges: [] };
  const hasGraph = Boolean(graph?.edges.length);

  return (
    <div className="app-shell min-h-screen text-foreground">
      <TopBar />

      <main className="relative z-10 mx-auto flex w-full max-w-[1600px] flex-col gap-6 px-4 pb-8 pt-4 sm:px-6 lg:gap-8 lg:px-10 lg:pb-10">
        <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.2fr_0.9fr]">
          <NatrualLanguageBox
            fun={setGraph}
            graph={graph}
            isParsing={isParsing}
            isOptimizing={isOptimizing}
            setIsParsing={setIsParsing}
            setIsOptimizing={setIsOptimizing}
          />
          <SNLBox
            graph={graph ?? emptyGraph}
            setGeneList={setGraph}
            geneColors={geneColors}
          />
        </section>

        <section className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(330px,0.8fr)]">
          <GeneNetworkGraph
            graph={graph}
            geneColors={geneColors}
            isBusy={isParsing || isOptimizing}
          />

          <aside className="animate-enter animate-delay-2 min-h-[320px]">
            <LogicalFormulasContainer
              lf={lf}
              setLF={setLF}
              geneColors={geneColors}
              onExport={exportGinml}
              isExporting={isExporting}
              hasGraph={hasGraph}
            />
          </aside>
        </section>
      </main>
    </div>
  );
}
