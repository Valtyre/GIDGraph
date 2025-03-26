import GeneInteractionBubble from "./Elements/geneInteractionBubble";

export function SNLBox(){


    return (
      <div className=" flex flex-col w-full p-5">
        <h1 className=" font-bold text-3xl text-white">
          Semi-Natrual Language
        </h1>
        <div className="flex flex-col p-5 gap-5 overflow-scroll bg-blue-900 border rounded-md">
          <GeneInteractionBubble geneInteraction={["GENE1", "inhibits", "GENE2"]}></GeneInteractionBubble>
          <GeneInteractionBubble geneInteraction={["GENE2", "activates", "GENE3"]}></GeneInteractionBubble>
          <GeneInteractionBubble geneInteraction={["GENE2", "activates", "GENE3"]}></GeneInteractionBubble>
          <GeneInteractionBubble geneInteraction={["GENE2", "activates", "GENE3"]}></GeneInteractionBubble>
          {/* <GeneInteractionBubble geneInteraction={["GENE2", "activates", "GENE3"]}></GeneInteractionBubble> */}
        </div>
      </div>
    );
}