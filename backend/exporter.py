"""
Minimal GINML (v2.2) exporter.

* Adds a circular node layout so new models open in GINsim with the
  nodes already spaced out.
* Works on Python ≥ 3.12 (serialises through *str* before pretty-print).
"""

from __future__ import annotations

import datetime
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Sequence, Tuple

from fastapi import APIRouter, Response

router = APIRouter()

# Public endpoint -------------------------------------------------------------

@router.post("/api/export_ginml")
def export_ginml(payload: dict) -> Response:
    """Convert *payload* to a downloadable GINML file."""

    graph = payload["graph"]
    formulas = payload["lf"]

    # collect every gene referenced in the model
    genes: set[str] = {f["targetGene"] for f in formulas}
    for edge in graph["edges"]:
        genes.update((edge["from"], edge["to"]))

    ordered_genes: List[str] = sorted(genes)  # reproducible output

    # build XML tree
    gxl = ET.Element("gxl", {"xmlns:xlink": "http://www.w3.org/1999/xlink"})
    graph_el = ET.SubElement(
        gxl,
        "graph",
        {
            "class": "regulatory",
            "id": "export_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "nodeorder": " ".join(ordered_genes),
        },
    )

    _add_default_styles(graph_el)
    _add_nodes(graph_el, ordered_genes, formulas)
    _add_edges(graph_el, graph["edges"])

    # serialise and pretty print
    rough_str = ET.tostring(gxl, encoding="unicode")
    pretty = minidom.parseString(rough_str).toprettyxml(indent="  ")
    doctype = '<!DOCTYPE gxl SYSTEM "http://ginsim.org/GINML_2_2.dtd">\n'
    xml_hdr, xml_body = pretty.split("\n", 1)
    final_bytes = (xml_hdr + "\n" + doctype + xml_body).encode("utf-8")

    headers = {"Content-Disposition": 'attachment; filename="model.ginml"'}
    return Response(content=final_bytes, media_type="application/xml", headers=headers)


# Helpers ---------------------------------------------------------------------

def _add_default_styles(graph_el: ET.Element) -> None:
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


def _add_nodes(graph_el: ET.Element, genes: Sequence[str], formulas: Sequence[dict]) -> None:
    """
    For each gene:
      - emit existing <parameter> tags for backwards compatibility
      - if there's a logical formula, build an expression string and emit:
          <value val="1">
            <exp str="..."/>
          </value>
      - then place the node visually
    """
    # map targetGene → formula dict
    formula_lookup: Dict[str, dict] = {f["targetGene"]: f for f in formulas}
    layout = _circular_layout(len(genes), centre=(300, 300), radius=200)

    for idx, gene in enumerate(genes):
        node_el = ET.SubElement(graph_el, "node", {"id": gene, "maxvalue": "1"})

        # 1) emit existing parameters
        if (formula := formula_lookup.get(gene)):
            for inc in formula["incomingGenes"]:
                sign = "" if inc["label"] else "!"
                param_id = f" {sign}{inc['gene']}:{gene}"
                ET.SubElement(
                    node_el,
                    "parameter",
                    {"idActiveInteractions": param_id, "val": "1"},
                )

            # 2) build and emit <value><exp/></value>
            parts: list[str] = []
            incs = formula["incomingGenes"]
            for i, inc in enumerate(incs):
                # build term with optional negation
                term = ("" if inc["label"] else "!") + inc["gene"]
                parts.append(term)
                # add connector after all but the last
                if i < len(incs) - 1:
                    connector = "&" if inc["truthValue"] else "|"
                    parts.append(f" {connector} ")

            expr = "".join(parts)

            # wrap OR-groups in parentheses for clarity if mixed with AND
            # (optional: more sophisticated parsing could be done here)

            value_el = ET.SubElement(node_el, "value", {"val": "1"})
            ET.SubElement(value_el, "exp", {"str": expr})

        # 3) place node visually
        x, y = layout[idx]
        ET.SubElement(
            node_el, "nodevisualsetting", {"x": str(x), "y": str(y), "style": ""}
        )


def _add_edges(graph_el: ET.Element, edges: Sequence[dict]) -> None:
    for e in edges:
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


def _circular_layout(
    n: int, *, centre: Tuple[int, int] = (300, 300), radius: int = 100
) -> List[Tuple[int, int]]:
    """Evenly space *n* points on a circle (integer coordinates)."""
    if n == 0:
        return []
    cx, cy = centre
    step = 2 * math.pi / n
    return [
        (int(cx + radius * math.cos(i * step)), int(cy + radius * math.sin(i * step)))
        for i in range(n)
    ]
