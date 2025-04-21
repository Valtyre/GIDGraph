# file: backend/parser_manager.py
import sys
import json

# Import existing NLP and parser functions
from .nlp.natural_language_processor import nlp_runner
from .parser.visParser import vis_parse_text

def process_nl_text(nl_text: str):
    """
    Master function to take any natural language text,
    run the NLP pipeline, parse it, and return (SNL, graph_dict).
    """
    # 1) Run NLP to get structured text/SNL
    nlp_output = nlp_runner(nl_text)

    # 2) Parse the result to build the graph
    transformer = vis_parse_text(nlp_output)

    # 3) Convert the graph to a vis.js-friendly dict, in memory
    graph_dict = transformer.get_vis_data()

    # 4) Return both the SNL text (nlp_output) and the graph data
    return nlp_output, graph_dict

def process_snl_only(snl_text: str) -> dict:
    """
    New function: takes already-edited SNL text,
    parses it with vis_parse_text, and returns the new graph dict.
    """
    transformer = vis_parse_text(snl_text)
    graph_dict = transformer.get_vis_data()
    return graph_dict
