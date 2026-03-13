"""
test_aggregation.py – Agregaciones temporales: horario, diario, semanal, mensual.

Cubre:
    - Agregación diaria ("diario", "D", "daily")
    - Agregación horaria ("horario", "H", "hourly")
    - Agregación semanal ("semanal", "W", "weekly")
    - Agregación mensual ("mensual", "M", "monthly")
    - Sin agregación (None, "raw")
    - Temperatura diaria → columnas [tiempo, valor, valor_media, valor_min, valor_max]
    - Precipitación diaria → se SUMA, no se promedia
    - Humedad diaria → se promedia
    - valor == valor_media siempre para temperatura
    - Cantidad de filas correcta (96/día raw → 1/día diario)
    - min ≤ media ≤ max
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION, VAR_HUMEDAD_RELATIVA
from helpers import FAKE_STATIONS, FAKE_VARIABLES_INIA47, _make_fake_data


def _client_con_datos(n_registros=96, var_id=2002, start="2025-01-01"):
    """Crea un client con datos fake y sin caché.

    Mockea los métodos del api directamente para que el mock
    persista durante toda la vida del cliente.
    """
    data = _make_fake_data(n_registros, var_id=var_id, start=start)
    client = INIAClient(api_key="fake", cache=False)
    client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
    client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
    client.api.get_data = MagicMock(return_value=data)
    return client


# ========================================================================
# 1. Aliases de agregación
# ========================================================================

class TestAliases:
    """Todos los aliases se resuelven correctamente."""

    @pytest.mark.parametrize("alias", ["diario", "D", "d", "daily"])
    def test_alias_diario(self, alias):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation=alias)
        assert len(df) == 1  # 1 día = 1 fila

    @pytest.mark.parametrize("alias", ["horario", "H", "h", "hourly"])
    def test_alias_horario(self, alias):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation=alias)
        assert len(df) == 24  # 1 día = 24 horas

    @pytest.mark.parametrize("alias", ["mensual", "M", "m", "monthly"])
    def test_alias_mensual(self, alias):
        client = _client_con_datos(2880, start="2025-01-01")  # 30 días
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-30", aggregation=alias)
        assert len(df) >= 1

    @pytest.mark.parametrize("alias", ["semanal", "W", "w", "weekly"])
    def test_alias_semanal(self, alias):
        client = _client_con_datos(672, start="2025-01-01")  # 7 días
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-07", aggregation=alias)
        assert len(df) >= 1

    def test_none_retorna_raw(self):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation=None)
        assert len(df) == 96

    def test_raw_string_retorna_raw(self):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="raw")
        assert len(df) == 96


# ========================================================================
# 2. Temperatura diaria: min, media, max
# ========================================================================

class TestTemperaturaDiaria:
    """Agregación diaria de temperatura produce [valor, valor_media, valor_min, valor_max]."""

    def test_columnas_temperatura_diaria(self):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="diario")
        assert "tiempo" in df.columns
        assert "valor" in df.columns
        assert "valor_min" in df.columns
        assert "valor_max" in df.columns
        assert "valor_media" in df.columns

    def test_valor_es_la_media(self):
        """'valor' debe ser igual a 'valor_media'."""
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="diario")
        pd.testing.assert_series_equal(df["valor"], df["valor_media"], check_names=False)

    def test_min_menor_igual_media(self):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="diario")
        assert (df["valor_min"] <= df["valor_media"]).all()

    def test_media_menor_igual_max(self):
        client = _client_con_datos(96)
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="diario")
        assert (df["valor_media"] <= df["valor_max"]).all()

    def test_min_max_media_coherentes(self):
        """min ≤ media ≤ max para todos los registros."""
        client = _client_con_datos(672)  # 7 días
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-07", aggregation="diario")
        assert len(df) == 7
        for _, row in df.iterrows():
            assert row["valor_min"] <= row["valor_media"] <= row["valor_max"]

    def test_7_dias_produce_7_filas(self):
        client = _client_con_datos(672, start="2025-01-01")  # 7 × 96
        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-07", aggregation="diario")
        assert len(df) == 7


# ========================================================================
# 3. Precipitación → SUMA
# ========================================================================

class TestPrecipitacionDiaria:
    """Precipitación se agrega con SUMA, no promedio."""

    def test_precipitacion_se_suma(self):
        """La suma diaria de precipitación > media."""
        n = 96
        rng = pd.date_range("2025-01-01", periods=n, freq="15min")
        data = [{"tiempo": t.isoformat(), "valor": "0.1"} for t in rng]

        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        df = client.get_data("INIA-47", VAR_PRECIPITACION, "2025-01-01", "2025-01-01", aggregation="diario")

        # suma = 96 × 0.1 = 9.6
        assert len(df) == 1
        assert abs(df["valor"].iloc[0] - 9.6) < 0.01

    def test_precipitacion_no_tiene_min_max(self):
        """Precipitación agregada no debería tener valor_min/valor_max."""
        data = _make_fake_data(96, var_id=2001)
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        df = client.get_data("INIA-47", VAR_PRECIPITACION, "2025-01-01", "2025-01-01", aggregation="diario")
        assert "valor_min" not in df.columns
        assert "valor_max" not in df.columns


# ========================================================================
# 4. Otras variables → PROMEDIO
# ========================================================================

class TestOtrasVariablesMedia:
    """Variables como humedad se agregan con promedio."""

    def test_humedad_se_promedia(self):
        n = 96
        rng = pd.date_range("2025-01-01", periods=n, freq="15min")
        data = [{"tiempo": t.isoformat(), "valor": "60.0"} for t in rng]

        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=data)

        df = client.get_data("INIA-47", VAR_HUMEDAD_RELATIVA, "2025-01-01", "2025-01-01", aggregation="diario")

        assert len(df) == 1
        assert abs(df["valor"].iloc[0] - 60.0) < 0.1


# ========================================================================
# 5. Agregación sobre datos vacíos
# ========================================================================

class TestAgregacionVacia:

    def test_datos_vacios_con_agregacion_no_crashea(self):
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
        client.api.get_data = MagicMock(return_value=[])

        df = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2025-01-01", "2025-01-01", aggregation="diario")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
