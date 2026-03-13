"""
test_edge_cases.py – Casos borde y escenarios inusuales.

Cubre:
    - parse_date con formatos válidos e inválidos
    - normalize_text con tildes y ñ
    - Datos con NaN / valores faltantes
    - DataFrame vacío a lo largo del pipeline
    - format_station_code
    - get_variable_info para variable desconocida
    - Estación con código raro
    - bulk_download con lista vacía
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import MagicMock, patch

from iniamet.utils import (
    parse_date,
    normalize_text,
    format_station_code,
    get_variable_info,
)
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
from iniamet.data import DataDownloader
from iniamet.api_client import APIClient
from tests.conftest import FAKE_STATIONS, FAKE_VARIABLES_INIA47, _make_fake_data


# ========================================================================
# 1. parse_date
# ========================================================================

class TestParseDate:

    def test_string_valido(self):
        result = parse_date("2025-06-15")
        assert result == datetime(2025, 6, 15)

    def test_datetime_input(self):
        dt = datetime(2025, 6, 15, 10, 30)
        assert parse_date(dt) == dt

    def test_date_input(self):
        d = date(2025, 6, 15)
        result = parse_date(d)
        assert isinstance(result, datetime)
        assert result.year == 2025

    def test_formato_invalido(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date("15/06/2025")

    def test_formato_invalido_ddmmyyyy(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date("15-06-2025")

    def test_tipo_invalido(self):
        with pytest.raises(TypeError):
            parse_date(12345)

    def test_string_vacio(self):
        with pytest.raises(ValueError):
            parse_date("")


# ========================================================================
# 2. normalize_text
# ========================================================================

class TestNormalizeText:

    def test_minusculas(self):
        assert normalize_text("HOLA") == "hola"

    def test_tildes(self):
        assert normalize_text("Ñuble") == "nuble"
        assert normalize_text("Biobío") == "biobio"
        assert normalize_text("Precipitación") == "precipitacion"

    def test_sin_cambios(self):
        assert normalize_text("test") == "test"


# ========================================================================
# 3. format_station_code
# ========================================================================

class TestFormatStationCode:

    def test_mayusculas(self):
        assert format_station_code("inia-47") == "INIA-47"

    def test_strip_espacios(self):
        assert format_station_code("  INIA-47  ") == "INIA-47"


# ========================================================================
# 4. Datos con NaN
# ========================================================================

class TestDatosConNaN:

    def test_valores_nan_no_crashean_agregacion(self):
        """Registros con valor NaN → no causan error en resample."""
        n = 96
        rng = pd.date_range("2025-01-01", periods=n, freq="15min")
        data = []
        for i, t in enumerate(rng):
            val = "NaN" if i % 10 == 0 else "15.5"
            data.append({"tiempo": t.isoformat(), "valor": val})

        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
                             "2025-01-01", "2025-01-01", aggregation="diario")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_todos_nan_produce_nan_en_agregacion(self):
        """Si todos los valores son NaN, la agregación produce NaN pero no falla."""
        n = 96
        rng = pd.date_range("2025-01-01", periods=n, freq="15min")
        data = [{"tiempo": t.isoformat(), "valor": "NaN"} for t in rng]

        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
                             "2025-01-01", "2025-01-01", aggregation="diario")
        assert len(df) == 1
        assert pd.isna(df["valor"].iloc[0])


# ========================================================================
# 5. DataFrame vacío en pipeline
# ========================================================================

class TestPipelineVacio:

    def test_get_stations_api_falla_retorna_vacio(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=[])
        df = client.get_stations()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_get_variables_api_falla_retorna_vacio(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_variables = MagicMock(return_value=[])
        df = client.get_variables("INIA-47")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_get_data_api_falla_retorna_vacio(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_data = MagicMock(return_value=None)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ========================================================================
# 6. bulk_download edge cases
# ========================================================================

class TestBulkEdgeCases:

    def test_bulk_lista_vacia_estaciones(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_data = MagicMock(return_value=_make_fake_data(96))
        result = client.bulk_download(
            stations=[],
            variables=[VAR_TEMPERATURA_MEDIA],
            start_date="2025-01-01",
            end_date="2025-01-01"
        )
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_bulk_lista_vacia_variables(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_data = MagicMock(return_value=_make_fake_data(96))
        result = client.bulk_download(
            stations=["INIA-47"],
            variables=[],
            start_date="2025-01-01",
            end_date="2025-01-01"
        )
        assert isinstance(result, dict)
        assert len(result) == 0


# ========================================================================
# 7. Variable info desconocida
# ========================================================================

class TestVariableInfoDesconocida:

    def test_variable_desconocida_retorna_placeholder(self):
        info = get_variable_info(99999)
        assert "nombre" in info
        assert "unidad" in info
        assert "99999" in info["nombre"]
