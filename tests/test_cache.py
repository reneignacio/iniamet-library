"""
test_cache.py – Sistema de caché: guardar, leer, limpiar.

Cubre:
    - Guardar y leer estaciones del caché
    - Guardar y leer variables del caché
    - Guardar y leer datos del caché
    - Caché no existe → retorna None
    - Limpiar caché
    - Directorio se crea automáticamente
    - Caché deshabilitado (cache=False)
    - Agregación funciona sobre datos cacheados
"""

import pytest
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

from iniamet.cache import CacheManager
from iniamet import INIAClient
from unittest.mock import patch
from tests.conftest import FAKE_STATIONS, FAKE_VARIABLES_INIA47, _make_fake_data


TEST_CACHE_DIR = "./test_iniamet_cache_tmp"


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Limpiar directorio de caché antes y después de cada test."""
    p = Path(TEST_CACHE_DIR)
    if p.exists():
        shutil.rmtree(p)
    yield
    if p.exists():
        shutil.rmtree(p)


# ========================================================================
# 1. CacheManager directo
# ========================================================================

class TestCacheManager:

    def test_crea_directorio_automaticamente(self):
        cm = CacheManager(TEST_CACHE_DIR)
        assert Path(TEST_CACHE_DIR).exists()
        assert (Path(TEST_CACHE_DIR) / "stations").exists()
        assert (Path(TEST_CACHE_DIR) / "variables").exists()
        assert (Path(TEST_CACHE_DIR) / "data").exists()

    def test_guardar_y_leer_estaciones(self):
        cm = CacheManager(TEST_CACHE_DIR)
        df = pd.DataFrame([
            {"codigo": "INIA-47", "nombre": "Ninhue", "region": "Ñuble"},
        ])
        cm.save_stations(df)
        result = cm.get_stations()
        assert result is not None
        assert len(result) == 1
        assert result["codigo"].iloc[0] == "INIA-47"

    def test_estaciones_no_cacheadas(self):
        cm = CacheManager(TEST_CACHE_DIR)
        result = cm.get_stations()
        assert result is None

    def test_guardar_y_leer_variables(self):
        cm = CacheManager(TEST_CACHE_DIR)
        df = pd.DataFrame([
            {"variable_id": 2002, "nombre": "Temperatura", "unidad": "°C"},
        ])
        cm.save_variables("INIA-47", df)
        result = cm.get_variables("INIA-47")
        assert result is not None
        assert len(result) == 1

    def test_variables_no_cacheadas(self):
        cm = CacheManager(TEST_CACHE_DIR)
        result = cm.get_variables("INIA-47")
        assert result is None

    def test_variables_otra_estacion(self):
        """Caché de variables es por estación."""
        cm = CacheManager(TEST_CACHE_DIR)
        df = pd.DataFrame([
            {"variable_id": 2002, "nombre": "Temperatura", "unidad": "°C"},
        ])
        cm.save_variables("INIA-47", df)
        # Otra estación → None
        result = cm.get_variables("INIA-139")
        assert result is None


# ========================================================================
# 2. Caché integrado con INIAClient
# ========================================================================

class TestCacheIntegration:

    def test_segunda_llamada_usa_cache(self):
        """Segunda llamada a get_stations() no llama a la API."""
        with patch("iniamet.api_client.APIClient._request") as mock_req:
            mock_req.return_value = FAKE_STATIONS
            client = INIAClient(api_key="fake", cache=True, cache_dir=TEST_CACHE_DIR)
            
            df1 = client.get_stations()
            call_count_1 = mock_req.call_count
            
            df2 = client.get_stations()
            call_count_2 = mock_req.call_count
            
            assert len(df1) == len(df2)
            # No debería haber llamadas adicionales a la API
            assert call_count_2 == call_count_1

    def test_cache_false_no_crea_directorio(self):
        """Con cache=False no se crea el directorio de caché."""
        import tempfile, os
        cache_path = os.path.join(tempfile.gettempdir(), "should_not_exist_cache")
        if Path(cache_path).exists():
            shutil.rmtree(cache_path)
        
        client = INIAClient(api_key="fake", cache=False, cache_dir=cache_path)
        assert not Path(cache_path).exists()

    def test_force_update_bypasses_cache(self):
        """force_update=True ignora el caché y llama a la API."""
        with patch("iniamet.api_client.APIClient._request") as mock_req:
            mock_req.return_value = FAKE_STATIONS
            client = INIAClient(api_key="fake", cache=True, cache_dir=TEST_CACHE_DIR)
            
            # Primera llamada → cachea
            client.get_stations()
            calls_after_first = mock_req.call_count
            
            # Segunda con force_update → llama a la API de nuevo
            client.get_stations(force_update=True)
            calls_after_force = mock_req.call_count
            
            assert calls_after_force > calls_after_first


# ========================================================================
# 3. Agregación sobre datos cacheados
# ========================================================================

class TestCacheConAgregacion:

    def test_agregacion_diaria_desde_cache(self):
        """Descargar raw, luego pedir diario → agrega desde caché."""
        data_raw = _make_fake_data(96, var_id=2002, start="2025-01-01")

        with patch("iniamet.api_client.APIClient._request") as mock_req:
            def _side(endpoint, params=None, retry=3):
                if endpoint == "estaciones":
                    return FAKE_STATIONS
                if endpoint == "variables":
                    return FAKE_VARIABLES_INIA47
                if endpoint == "muestras":
                    return data_raw
                return None
            mock_req.side_effect = _side
            client = INIAClient(api_key="fake", cache=True, cache_dir=TEST_CACHE_DIR)

            # Primera llamada → raw → se cachea
            df_raw = client.get_data("INIA-47", 2002, "2025-01-01", "2025-01-01")
            assert len(df_raw) == 96

            # Segunda llamada con agregación → debería usar caché
            df_daily = client.get_data("INIA-47", 2002, "2025-01-01", "2025-01-01", aggregation="diario")
            assert len(df_daily) == 1
            assert "valor_min" in df_daily.columns
            assert "valor_max" in df_daily.columns
