from lark import Lark, Transformer, UnexpectedInput
import networkx as nx

# Load the grammar from file
try:
    with open("gene_snl.lark", "r") as f:
        gene_snl_grammar = f.read()
except FileNotFoundError:
    print("Error: The file 'gene_snl.lark' was not found.")
    print("Make sure the grammar file is in the correct folder.")
    exit(1)

# Create the Lark parser
gene_parser = Lark(gene_snl_grammar, parser='lalr', start='start')

# Transformer class
class GeneTransformer(Transformer):
    def __init__(self):
        self.graph = nx.DiGraph()

    def gene(self, items):
        return str(items[0])  # Convert gene names to strings

    def activation(self, items):
        source, target = items  # Now only gets gene names
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
        #nx.write_graphml_lxml(self.graph, filename)
        print(f"GraphML file saved as {filename}")

# Example input
example_snl = """
GATA46 activates HAND2.
GATA46 inhibits HEY2.
IRX4 activates HAND2.
NR2F2 inhibits IRX4.
HEY2 knockout leads to MYL7.
"""

# Try to parse the input and handle errors
try:
    tree = gene_parser.parse(example_snl)
    #print(tree.pretty())
except UnexpectedInput as e:
    print("\n🚨 ERROR: Invalid sentence structure! 🚨")
    print(f"🔍 Problem at position {e.pos_in_stream}: {e.get_context(example_snl)}")
    print("🔹 Possible solution: Check for extra/missing words.")
    exit(1)

# Transform and save the graph
transformer = GeneTransformer()
transformer.transform(tree)
transformer.to_graphml("gene_network.graphml")

