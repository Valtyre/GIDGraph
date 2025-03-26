

export default function GeneInteractionBubble({ geneInteraction }: { geneInteraction: [string, string, string] }) {

    const [gene1, interaction, gene2] = geneInteraction

    if (interaction == "activates") {
        var other = "inhibits"
    } else {
        var other = "activates"
    }

    function GeneText({name} : {name: string}){
        return (
            <>
            <span className="text-center flex-1 text-2xl">
                {name}
            </span>
            
            </>
        )


    }
    return (
        <div className="flex items-center justify-center mx-auto w-full p-5 gap-5 bg-blue-200 rounded-md">
            <GeneText name={gene1}></GeneText>

            <div className="flex-1 flex justify-center">
                <select
                name="interaction"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-center w-fit rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-50"
                >
                <option value={interaction}>{interaction}</option>
                <option value={other}>{other}</option>
                </select>
            </div>
            <GeneText name={gene2}></GeneText>
        </div>        
    );
      
}
