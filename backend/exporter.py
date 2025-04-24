# backend/exporter.py
"""
Builds a minimal GINML file from the graph + logical-formula data
sent by the frontend.   POST /api/export_ginml  returns the file
as an XML download (Content-Disposition: attachment).
"""

import datetime, io
import xml.etree.ElementTree as ET
from xml.dom import minidom     
from fastapi import APIRouter, Response

router = APIRouter()


@router.post("/api/export_ginml")
def export_ginml(payload: dict):
    """
    Expected payload JSON
    {
      "graph": { "edges": [ {id, from, to, label}, ... ] },
      "lf": [
        { "targetGene": "A",
          "incomingGenes": [
             { "gene": "B", "label": true,  "truthValue": true },
             { "gene": "C", "label": false, "truthValue": true }
          ]
        },
        ...
      ]
    }
    """
    graph = payload["graph"]
    lf    = payload["lf"]

    # ── root <gxl><graph> ──────────────────────────────
    gxl = ET.Element(
        "gxl", {"xmlns:xlink": "http://www.w3.org/1999/xlink"}
    )
    
    
    genes = set(f["targetGene"] for f in lf)

    for e in graph["edges"]:
        genes.add(e["from"])
        genes.add(e["to"])
    
    
    graph_el = ET.SubElement(
        gxl,
        "graph",
        {
            "class": "regulatory",
            "id": "export_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "nodeorder": " ".join(genes),
        },
    )

    # generic node / edge style blocks (optional)
    ET.SubElement(
        graph_el,
        "nodestyle",
        {
            "background": "#ffffff",
            "foreground": "#000000",
            "text": "#000000",
            "shape": "RECTANGLE",
            "width": "45",
            "height": "25",
        },
    )
    ET.SubElement(
        graph_el,
        "edgestyle",
        {
            "color": "#000000",
            "pattern": "SIMPLE",
            "line_width": "1",
            "properties": "positive:#00c800 negative:#c80000 dual:#0000c8",
        },
    )

    # ── nodes + parameters from logical formulas ───────
    
    formula_lookup = {f["targetGene"]: f for f in lf} # for quick access
    
    for gene in genes:
        node_el = ET.SubElement(graph_el, "node", {"id": gene, "maxvalue": "1"})
        
        formula = formula_lookup.get(gene)
        
        if formula:
            for inc in formula["incomingGenes"]:
                sign = "" if inc["label"] else "!"
                param_id = f" {sign}{inc['gene']}:{gene}"
                ET.SubElement(
                    node_el,
                    "parameter",
                    {"idActiveInteractions": param_id, "val": "1"},
            )
        
        
    # ── edges from graph.edges ─────────────────────────
    for e in graph["edges"]:
        sign = "positive" if e["label"] == "activation" else "negative"
        ET.SubElement(
            graph_el,
            "edge",
            {
                "id": f"{e['from']}:{e['to']}",
                "from": e["from"],
                "to": e["to"],
                "minvalue": "1",
                "sign": sign,
            },
        )

    # ── serialize & pretty-print ─────────────────────────
    rough = ET.tostring(gxl, encoding="utf-8")

    pretty = minidom.parseString(rough).toprettyxml(indent="  ")

    # prepend the required DOCTYPE line
    doctype = '<!DOCTYPE gxl SYSTEM "http://ginsim.org/GINML_2_2.dtd">\n'

    pretty  = minidom.parseString(rough).toprettyxml(indent="  ")
    parts   = pretty.split("\n", 1)                  # ["<?xml …?>", rest]
    xml_str = parts[0] + "\n" + doctype + parts[1]   # insert doctype after header
    xml_bytes = xml_str.encode("utf-8")

    headers = {"Content-Disposition": 'attachment; filename="model.ginml"'}
    return Response(content=xml_bytes, media_type="application/xml", headers=headers)