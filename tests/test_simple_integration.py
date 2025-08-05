"""
Basic Integration Tests for WhatsPayAI Application
"""

import pytest

from src.app import app


class TestBasicIntegration:
    """Basic integration tests that don't require TestClient."""

    def test_app_creation(self):
        """Test that the FastAPI app is created successfully."""
        assert app is not None
        assert app.title == "WhatsPayAI"

    def test_app_routes(self):
        """Test that required routes are registered."""
        route_paths = [route.path for route in app.routes]
        assert "/webhook" in route_paths
        assert "/" in route_paths
        assert "/stats" in route_paths
