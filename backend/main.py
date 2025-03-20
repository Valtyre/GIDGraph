import json
from parser.parser import parse_text  # Import the parsing function
from nlp.spacy_test import nlp_runner  # Import the NLP pipeline

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
    transformer = parse_text(nlp_output)

    # Save the output graph
    transformer.to_graphml("gene_network.graphml")

    print("\n✅ Parsing complete! GraphML file generated.")

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
