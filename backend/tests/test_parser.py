"""
Unit tests for the SNL parser (visParser).
"""
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest


class TestVisParser:
    """Tests for the visParser module."""

    def test_parse_activation(self):
        """Test parsing activation statement."""
        from backend.parser.visParser import vis_parse_text
        
        result = vis_parse_text("GATA4 activates HAND2.")
        graph_data = result.get_vis_data()
        
        assert len(graph_data["nodes"]) == 2
        assert len(graph_data["edges"]) == 1
        assert graph_data["edges"][0]["label"] == "activation"

    def test_parse_inhibition(self):
        """Test parsing inhibition statement."""
        from backend.parser.visParser import vis_parse_text
        
        result = vis_parse_text("NR2F2 inhibits IRX4.")
        graph_data = result.get_vis_data()
        
        assert len(graph_data["nodes"]) == 2
        assert len(graph_data["edges"]) == 1
        assert graph_data["edges"][0]["label"] == "inhibition"

    def test_parse_multiple_statements(self):
        """Test parsing multiple statements."""
        from backend.parser.visParser import vis_parse_text
        
        snl = "GATA4 activates HAND2. NR2F2 inhibits IRX4."
        result = vis_parse_text(snl)
        graph_data = result.get_vis_data()
        
        assert len(graph_data["nodes"]) == 4
        assert len(graph_data["edges"]) == 2

    def test_parse_knockout(self):
        """Test parsing knockout statement."""
        from backend.parser.visParser import vis_parse_text
        
        result = vis_parse_text("HAND2 knockout inhibits IRX4.")
        graph_data = result.get_vis_data()
        
        assert len(graph_data["edges"]) == 1
        assert graph_data["edges"][0]["label"] == "knockout inhibition"

    def test_parse_binding(self):
        """Test parsing binding statement."""
        from backend.parser.visParser import vis_parse_text
        
        result = vis_parse_text("GATA4 binds HAND2.")
        graph_data = result.get_vis_data()
        
        assert len(graph_data["edges"]) == 1
        assert graph_data["edges"][0]["label"] == "binding"

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        from backend.parser.visParser import vis_parse_text
        
        # Empty string should raise an error or return empty graph
        with pytest.raises(Exception):
            vis_parse_text("")
