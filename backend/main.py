import json
#from parser.parser import parse_text  # Import the parsing function
from parser.visParser import vis_parse_text  # Import the parsing function from the visual parser
from backend.nlp.natural_language_processor import nlp_runner  # Import the NLP pipeline

def main():
    # Load NLP text from JSON
    try:
        with open("backend/nlp/nl_texts.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'nl_texts.json' was not found.")
        exit(1)

    # Run NLP pipeline and get structured text
    nlp_output = nlp_runner(data["text3"])

    # Debugging: Print NLP output to confirm correct format
    print("🔹 NLP Output:\n", nlp_output)

    # Run the parser
    transformer = vis_parse_text(nlp_output)

    # Save the output graph
    #transformer.to_graphml("backend/graphOutputs/gene_network.graphml")
    transformer.to_json("backend/graphOutputs/gene_network.json")


    print("\n✅ Parsing complete! GraphML file generated.")

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
