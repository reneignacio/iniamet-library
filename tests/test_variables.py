"""
test_variables.py – Consulta de variables por estación.

Cubre:
    - Variables de una estación conocida
    - Columnas esperadas (variable_id, nombre, unidad)
    - Variable que existe en la estación
    - Variable que NO existe en la estación
    - Validar por ID numérico y por string
    - Buscar variable por nombre (fuzzy)
    - Estación sin variables → DataFrame vacío
    - Constantes de variable (VAR_TEMPERATURA_MEDIA, etc.)
    - Listado completo de variables (list_all_variables)
    - is_valid_variable_id
    - get_variable_info
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock

from iniamet import (
    INIAClient,
    VAR_TEMPERATURA_MEDIA,
    VAR_PRECIPITACION,
    VAR_HUMEDAD_RELATIVA,
    VAR_RADIACION_MEDIA,
    VAR_VIENTO_VELOCIDAD_MEDIA,
    VAR_PRESION_ATMOSFERICA,
    list_all_variables,
    is_valid_variable_id,
    get_variable_info,
    get_variable_id_by_name,
)
from helpers import FAKE_STATIONS, FAKE_VARIABLES_INIA47


def _make_client():
    """Crea un INIAClient con métodos de api mockeados directamente."""
    client = INIAClient(api_key="fake", cache=False)
    client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
    client.api.get_variables = MagicMock(return_value=FAKE_VARIABLES_INIA47)
    return client


# ========================================================================
# 1. get_variables
# ========================================================================

class TestGetVariables:

    def test_variables_retorna_dataframe(self):
        client = _make_client()
        df = client.get_variables("INIA-47")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_columnas_esperadas(self):
        client = _make_client()
        df = client.get_variables("INIA-47")
        assert {"variable_id", "nombre", "unidad"}.issubset(set(df.columns))

    def test_temperatura_en_variables(self):
        client = _make_client()
        df = client.get_variables("INIA-47")
        ids = df["variable_id"].tolist()
        assert VAR_TEMPERATURA_MEDIA in ids

    def test_precipitacion_en_variables(self):
        client = _make_client()
        df = client.get_variables("INIA-47")
        ids = df["variable_id"].tolist()
        assert VAR_PRECIPITACION in ids

    def test_estacion_sin_variables(self):
        """Estación sin variables → DataFrame vacío."""
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
        client.api.get_variables = MagicMock(return_value=[])
        df = client.get_variables("FAKE-999")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ========================================================================
# 2. validate_station_variable
# ========================================================================

class TestValidateStationVariable:

    def test_variable_existente_por_id_int(self):
        client = _make_client()
        assert client.validate_station_variable("INIA-47", VAR_TEMPERATURA_MEDIA) is True

    def test_variable_existente_por_id_str(self):
        client = _make_client()
        assert client.validate_station_variable("INIA-47", "2002") is True

    def test_variable_inexistente_por_id(self):
        client = _make_client()
        assert client.validate_station_variable("INIA-47", 9999) is False

    def test_variable_existente_por_nombre(self):
        client = _make_client()
        assert client.validate_station_variable("INIA-47", "temperatura") is True

    def test_variable_inexistente_por_nombre(self):
        client = _make_client()
        assert client.validate_station_variable("INIA-47", "ozono") is False


# ========================================================================
# 3. Constantes de variable
# ========================================================================

class TestConstantesVariable:

    def test_valores_constantes(self):
        """Las constantes deben tener los IDs esperados."""
        assert VAR_TEMPERATURA_MEDIA == 2002
        assert VAR_PRECIPITACION == 2001
        assert VAR_HUMEDAD_RELATIVA == 2007
        assert VAR_RADIACION_MEDIA == 2022
        assert VAR_VIENTO_VELOCIDAD_MEDIA == 2013
        assert VAR_PRESION_ATMOSFERICA == 2125


# ========================================================================
# 4. Funciones de utilidad de variables
# ========================================================================

class TestVariableUtils:

    def test_list_all_variables_retorna_df(self):
        df = list_all_variables()
        assert isinstance(df, pd.DataFrame)
        assert "variable_id" in df.columns
        assert "nombre" in df.columns
        assert len(df) > 0

    def test_is_valid_variable_id_true(self):
        assert is_valid_variable_id(VAR_TEMPERATURA_MEDIA) is True

    def test_is_valid_variable_id_false(self):
        assert is_valid_variable_id(99999) is False

    def test_get_variable_info_conocida(self):
        info = get_variable_info(VAR_TEMPERATURA_MEDIA)
        assert "nombre" in info
        assert "unidad" in info
        assert info["nombre"] == "Temperatura del Aire Media"

    def test_get_variable_info_desconocida(self):
        info = get_variable_info(99999)
        assert "nombre" in info
        assert "99999" in info["nombre"]

    def test_get_variable_id_by_name_temperatura(self):
        result = get_variable_id_by_name("temperatura")
        assert result == VAR_TEMPERATURA_MEDIA

    def test_get_variable_id_by_name_precipitacion(self):
        result = get_variable_id_by_name("precipitacion")
        assert result == VAR_PRECIPITACION

    def test_get_variable_id_by_name_inexistente(self):
        result = get_variable_id_by_name("ozono estratosferico")
        assert result is None
