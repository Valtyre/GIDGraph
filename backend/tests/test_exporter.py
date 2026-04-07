"""
Unit tests for the GINML exporter.
"""
import pytest
from xml.etree import ElementTree as ET


class TestExporter:
    """Tests for the exporter module."""

    def test_export_ginml_valid(self, api_client, sample_graph, sample_logical_formulas):
        """Test exporting valid graph to GINML."""
        payload = {
            "graph": sample_graph,
            "logicalFormulas": sample_logical_formulas
        }
        response = api_client.post("/api/export_ginml", json=payload)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml; charset=utf-8"
        
        # Verify XML is valid
        xml_content = response.content.decode("utf-8")
        root = ET.fromstring(xml_content)
        assert root.tag == "gxl"

    def test_export_ginml_empty_graph(self, api_client):
        """Test exporting empty graph."""
        payload = {
            "graph": {"nodes": [], "edges": []},
            "logicalFormulas": []
        }
        response = api_client.post("/api/export_ginml", json=payload)
        
        assert response.status_code == 200

    def test_export_ginml_missing_graph(self, api_client):
        """Test error when graph is missing."""
        payload = {
            "logicalFormulas": []
        }
        response = api_client.post("/api/export_ginml", json=payload)
        
        # Should return error (422 for validation or 400 for bad request)
        assert response.status_code in [400, 422, 500]

    def test_export_ginml_xml_structure(self, api_client, sample_graph, sample_logical_formulas):
        """Test GINML XML has correct structure."""
        payload = {
            "graph": sample_graph,
            "logicalFormulas": sample_logical_formulas
        }
        response = api_client.post("/api/export_ginml", json=payload)
        
        xml_content = response.content.decode("utf-8")
        root = ET.fromstring(xml_content)
        
        # Check for graph element
        graph = root.find("graph")
        assert graph is not None
        
        # Check for nodes
        nodes = graph.findall("node")
        assert len(nodes) == len(sample_graph["nodes"])
