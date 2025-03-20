from lark import Lark, Transformer, UnexpectedInput
import networkx as nx

# Load the grammar from file
def load_grammar():
    try:
        with open("backend/parser/gene_snl.lark", "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: The file 'gene_snl.lark' was not found.")
        exit(1)

# Create the Lark parser
gene_parser = Lark(load_grammar(), parser='lalr', start='start')

# Transformer class
class GeneTransformer(Transformer):
    def __init__(self):
        self.graph = nx.DiGraph()

    def gene(self, items):
        return str(items[0])  # Convert gene names to strings

    def activation(self, items):
        source, target = items
        self.graph.add_edge(source, target, label="activation")

    def inhibition(self, items):
        source, target = items
        self.graph.add_edge(source, target, label="inhibition")

    def knockout(self, items):
        source, target = items
        self.graph.add_edge(source, target, label="knockout inhibition")

    def binding(self, items):
        source, target = items
        self.graph.add_edge(source, target, label="binding")

    def to_graphml(self, filename="gene_network.graphml"):
        nx.write_graphml(self.graph, filename)
        print(f"GraphML file saved as {filename}")

# Function to parse input text
def parse_text(input_text):
    try:
        tree = gene_parser.parse(input_text)
    except UnexpectedInput as e:
        print("\n🚨 ERROR: Invalid sentence structure! 🚨")
        print(f"🔍 Problem at position {e.pos_in_stream}: {e.get_context(input_text)}")
        print("🔹 Possible solution: Check for extra/missing words.")
        exit(1)

    # Transform and return the graph
    transformer = GeneTransformer()
    transformer.transform(tree)
    return transformer
