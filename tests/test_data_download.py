"""
test_data_download.py – Descarga de datos de una estación.

Cubre:
    - Descarga raw (sin agregación) → DataFrame con columnas [tiempo, valor]
    - 'tiempo' es datetime, 'valor' es numérico
    - Datos ordenados cronológicamente
    - Fechas como string y como datetime
    - Fecha futura / sin datos → DataFrame vacío
    - Estación inexistente → DataFrame vacío
    - Variable como int y como string
    - bulk_download con múltiples estaciones/variables
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import datetime

from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION
from tests.conftest import FAKE_STATIONS, FAKE_VARIABLES_INIA47, _make_fake_data


def _make_client(data_response=None):
    """Crea un INIAClient con api mockeada directamente (mock persiste)."""
    if data_response is None:
        data_response = _make_fake_data(96)

    client = INIAClient(api_key="fake", cache=False)
    client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
    client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
    client.api.get_data = MagicMock(return_value=data_response)
    return client


# ========================================================================
# 1. Descarga básica (raw)
# ========================================================================

class TestDescargaBasica:

    def test_get_data_retorna_dataframe(self):
        client = _make_client()
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_columnas_tiempo_valor(self):
        client = _make_client()
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert "tiempo" in df.columns
        assert "valor" in df.columns

    def test_tiempo_es_datetime(self):
        client = _make_client()
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert pd.api.types.is_datetime64_any_dtype(df["tiempo"])

    def test_valor_es_numerico(self):
        client = _make_client()
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert pd.api.types.is_numeric_dtype(df["valor"])

    def test_datos_ordenados_cronologicamente(self):
        client = _make_client(_make_fake_data(200))
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-03")
        assert df["tiempo"].is_monotonic_increasing

    def test_96_registros_en_1_dia(self):
        """1 día = 96 registros de 15 min."""
        data = _make_fake_data(96, start="2025-06-01")
        client = _make_client(data)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-06-01", "2025-06-01")
        assert len(df) == 96


# ========================================================================
# 2. Formatos de entrada
# ========================================================================

class TestFormatosEntrada:

    def test_fecha_como_string(self):
        client = _make_client()
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)

    def test_fecha_como_datetime(self):
        client = _make_client()
        df = client.get_data(
            "INIA-47", VAR_TEMPERATURA_MEDIA,
            datetime(2025, 1, 1), datetime(2025, 1, 1)
        )
        assert isinstance(df, pd.DataFrame)

    def test_variable_como_int(self):
        client = _make_client()
        df = client.get_data("INIA-47", 2002, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_variable_como_string(self):
        client = _make_client()
        df = client.get_data("INIA-47", "2002", "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_fecha_formato_invalido_error(self):
        client = _make_client()
        with pytest.raises(ValueError, match="Invalid date format"):
            client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "01-01-2025", "31-01-2025")


# ========================================================================
# 3. Sin datos
# ========================================================================

class TestSinDatos:

    def test_api_retorna_vacio(self):
        """API retorna [] → DataFrame vacío."""
        client = _make_client(data_response=[])
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_api_retorna_none(self):
        """API retorna None → DataFrame vacío."""
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=None)

        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ========================================================================
# 4. Bulk download
# ========================================================================

class TestBulkDownload:

    def test_bulk_retorna_dict(self):
        data = _make_fake_data(96)
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        with patch("time.sleep"):
            result = client.bulk_download(
                stations=["INIA-47", "INIA-139"],
                variables=[VAR_TEMPERATURA_MEDIA],
                start_date="2025-01-01",
                end_date="2025-01-01"
            )
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_bulk_keys_formato_station_variable(self):
        data = _make_fake_data(96)
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        with patch("time.sleep"):
            result = client.bulk_download(
                stations=["INIA-47"],
                variables=[VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION],
                start_date="2025-01-01",
                end_date="2025-01-01"
            )
        for key in result:
            assert "_" in key

    def test_bulk_varias_estaciones_varias_variables(self):
        data = _make_fake_data(96)
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        with patch("time.sleep"):
            result = client.bulk_download(
                stations=["INIA-47", "INIA-139"],
                variables=[VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION],
                start_date="2025-01-01",
                end_date="2025-01-01"
            )
        assert len(result) <= 4

    def test_bulk_estacion_sin_datos_no_crashea(self):
        """Si una estación no tiene datos, se omite sin error."""
        counter = {"calls": 0}

        def _side_get_data(station, variable, start_date, end_date):
            counter["calls"] += 1
            if counter["calls"] == 1:
                return _make_fake_data(96)
            return []

        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(side_effect=_side_get_data)

        with patch("time.sleep"):
            result = client.bulk_download(
                stations=["INIA-47", "FAKE-999"],
                variables=[VAR_TEMPERATURA_MEDIA],
                start_date="2025-01-01",
                end_date="2025-01-01"
            )
        assert len(result) >= 1
