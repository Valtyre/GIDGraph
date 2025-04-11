import sys
import json
import networkx as nx
from lark import Lark, Transformer, UnexpectedInput

def load_grammar(grammar_path="backend/parser/gene_snl.lark") -> str:
    """
    Load and return the grammar from a file.

    Args:
        grammar_path (str): The path to the grammar file.

    Returns:
        str: The contents of the grammar file.

    Exits:
        Exits the program if the file is not found.
    """
    try:
        with open(grammar_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{grammar_path}' was not found.")
        sys.exit(1)

# Initialize the Lark parser using the loaded grammar.
grammar = load_grammar()
gene_parser = Lark(grammar, parser='lalr', start='start')

class GeneTransformer(Transformer):
    """
    Transformer to build a gene interaction graph from a parse tree.
    """
    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()

    def gene(self, items):
        # Convert gene names to strings.
        return str(items[0])

    def activation(self, items):
        source, target = items
        self.graph.add_edge(source, target,
                            label="activation")

    def inhibition(self, items):
        source, target = items
        self.graph.add_edge(source, target,
                            label="inhibition")

    def knockout(self, items):
        source, target = items
        self.graph.add_edge(source, target,
                            label="knockout inhibition")

    def binding(self, items):
        source, target = items
        self.graph.add_edge(source, target,
                            label="binding")

    def to_json(self, filename="backend/graphOutputs/gene_network.json"):
        """
        Exports the graph to a JSON file in a vis.js compatible format.
        """
        graph_data = self.get_vis_data()  # <-- We'll reuse the new helper method
        with open(filename, "w") as f:
            json.dump(graph_data, f, indent=4)
        print(f"Graph JSON saved as {filename}")

    def get_vis_data(self):
        """
        Returns the graph in a vis.js-friendly dictionary (without writing to file).
        """
        nodes = [{"id": node, "label": node} 
                 for node in self.graph.nodes]
        
        edges = []
        for u, v, d in self.graph.edges(data=True):
            edge_data = {
                "from": u,
                "to": v,
                "label": d.get("label", ""),
            }


            edges.append(edge_data)

        return {"nodes": nodes, "edges": edges}

def vis_parse_text(input_text: str) -> GeneTransformer:
    """
    Parses the input text to generate a gene interaction graph.

    Args:
        input_text (str): The input text to parse.

    Returns:
        GeneTransformer: The transformer containing the graph.
    """
    try:
        tree = gene_parser.parse(input_text)
    except UnexpectedInput as e:
        print("\n🚨 ERROR: Invalid sentence structure! 🚨")
        print(f"🔍 Problem at position {e.pos_in_stream}: {e.get_context(input_text)}")
        print("🔹 Possible solution: Check for extra/missing words.")
        sys.exit(1)

    transformer = GeneTransformer()
    transformer.transform(tree)
    return transformer
