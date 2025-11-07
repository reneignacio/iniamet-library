"""
Test configuration and fixtures for pytest.
"""
import pytest


@pytest.fixture
def sample_cache_dir(tmp_path):
    """Create a temporary cache directory for tests."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def mock_api_response():
    """Sample API response for testing."""
    return {
        "estaciones": [
            {
                "codigo": "INIA-47",
                "nombre": "Chillán",
                "latitud": -36.6033,
                "longitud": -71.9117,
                "elevacion": 151,
                "region": "Ñuble"
            }
        ]
    }


@pytest.fixture
def sample_station_data():
    """Sample station data for testing."""
    return {
        "codigo": "INIA-47",
        "nombre": "Chillán",
        "latitud": -36.6033,
        "longitud": -71.9117,
        "elevacion": 151,
        "region": "Ñuble",
        "comuna": "Chillán",
        "tipo": "INIA"
    }
