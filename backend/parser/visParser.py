import json
from dataclasses import dataclass

import networkx as nx
from lark import Lark, Transformer, UnexpectedInput


@dataclass(frozen=True)
class ParserError(ValueError):
    error: str
    message: str
    original_input: str
    parser_input: str
    position: int | None = None
    context: str | None = None


def load_grammar(grammar_path="backend/parser/gene_snl.lark") -> str:
    """
    Load and return the grammar from a file.

    Args:
        grammar_path (str): The path to the grammar file.

    Returns:
        str: The contents of the grammar file.
    """
    try:
        with open(grammar_path, "r") as f:
            return f.read()
    except FileNotFoundError as exc:
        raise RuntimeError(f"The grammar file '{grammar_path}' was not found.") from exc


grammar = load_grammar()
gene_parser = Lark(grammar, parser="lalr", start="start")


class GeneTransformer(Transformer):
    """
    Transformer to build a gene interaction graph from a parse tree.
    """

    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()

    def gene(self, items):
        return str(items[0])

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

    def to_json(self, filename="backend/graphOutputs/gene_network.json"):
        """
        Exports the graph to a JSON file in a vis.js compatible format.
        """
        graph_data = self.get_vis_data()
        with open(filename, "w") as f:
            json.dump(graph_data, f, indent=4)
        print(f"Graph JSON saved as {filename}")

    def get_vis_data(self):
        """
        Returns the graph in a vis.js-friendly dictionary (without writing to file).
        """
        nodes = [{"id": node, "label": node} for node in self.graph.nodes]

        edges = []
        for u, v, d in self.graph.edges(data=True):
            edges.append(
                {
                    "from": u,
                    "to": v,
                    "label": d.get("label", ""),
                }
            )

        return {"nodes": nodes, "edges": edges}


def vis_parse_text(input_text: str, *, original_input: str | None = None) -> GeneTransformer:
    """
    Parses parser-ready semi-natural language into a gene interaction graph.

    Args:
        input_text (str): Canonical parser-ready text.
        original_input (str | None): Optional source text before normalization.

    Returns:
        GeneTransformer: The transformer containing the graph.
    """
    parser_input = input_text.strip()
    source_input = input_text if original_input is None else original_input

    if not parser_input:
        raise ParserError(
            error="NO_VALID_RELATIONS",
            message="No valid parser-ready gene relations were found.",
            original_input=source_input,
            parser_input=parser_input,
        )

    try:
        tree = gene_parser.parse(parser_input)
    except UnexpectedInput as exc:
        raise ParserError(
            error="INVALID_SNL",
            message="The extracted semi-natural language is not valid for the parser.",
            original_input=source_input,
            parser_input=parser_input,
            position=exc.pos_in_stream,
            context=exc.get_context(parser_input),
        ) from exc

    transformer = GeneTransformer()
    transformer.transform(tree)
    return transformer
