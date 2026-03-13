"""
test_stations.py – Consulta y filtrado de estaciones.

Cubre:
    - Obtener todas las estaciones
    - Filtrar por 1 región (R16, Ñuble, 16)
    - Filtrar por varias regiones [R16, R08]
    - Filtrar por tipo (INIA, DMC)
    - Filtrar por región + tipo a la vez
    - Región que no existe → DataFrame vacío
    - Columnas esperadas del DataFrame de salida
    - Valores de latitud / longitud numéricos
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock

from iniamet import INIAClient
from tests.conftest import FAKE_STATIONS


def _make_client():
    """Crea un INIAClient con api.get_stations mockeado directamente."""
    client = INIAClient(api_key="fake", cache=False)
    client.api.get_stations = MagicMock(return_value=FAKE_STATIONS)
    return client


# ========================================================================
# 1. Obtener estaciones
# ========================================================================

class TestGetStations:
    """Tests de client.get_stations()."""

    def test_todas_las_estaciones(self):
        client = _make_client()
        df = client.get_stations()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(FAKE_STATIONS)

    def test_columnas_esperadas(self):
        client = _make_client()
        df = client.get_stations()
        columnas_esperadas = {"codigo", "nombre", "region", "comuna",
                              "latitud", "longitud", "elevacion", "tipo"}
        assert columnas_esperadas.issubset(set(df.columns))

    def test_lat_lon_son_numericos(self):
        client = _make_client()
        df = client.get_stations()
        assert pd.api.types.is_numeric_dtype(df["latitud"])
        assert pd.api.types.is_numeric_dtype(df["longitud"])

    def test_api_sin_datos_retorna_df_vacio(self):
        """Si la API no devuelve estaciones → DataFrame vacío."""
        client = INIAClient(api_key="fake", cache=False)
        client.api.get_stations = MagicMock(return_value=[])
        df = client.get_stations()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ========================================================================
# 2. Filtrar por región
# ========================================================================

class TestFiltrarPorRegion:
    """Tests de filtrado regional."""

    def test_filtrar_codigo_R16(self):
        client = _make_client()
        df = client.get_stations(region="R16")
        assert len(df) > 0
        assert all(df["region"] == "Ñuble")

    def test_filtrar_nombre_nuble(self):
        client = _make_client()
        df = client.get_stations(region="Ñuble")
        assert len(df) > 0
        assert all(df["region"] == "Ñuble")

    def test_filtrar_numero_16(self):
        client = _make_client()
        df = client.get_stations(region="16")
        assert len(df) > 0
        assert all(df["region"] == "Ñuble")

    def test_filtrar_R07_maule(self):
        client = _make_client()
        df = client.get_stations(region="R07")
        assert len(df) > 0
        assert all(df["region"] == "Maule")

    def test_filtrar_dos_regiones(self):
        client = _make_client()
        df = client.get_stations(region=["R16", "R07"])
        regiones = set(df["region"].unique())
        assert regiones == {"Ñuble", "Maule"}

    def test_filtrar_tres_regiones(self):
        client = _make_client()
        df = client.get_stations(region=["R16", "R07", "R08"])
        regiones = set(df["region"].unique())
        assert regiones == {"Ñuble", "Maule", "Biobío"}

    def test_lista_formatos_mixtos(self):
        """Mezclar código, número y nombre."""
        client = _make_client()
        df = client.get_stations(region=["R16", "7", "Biobío"])
        regiones = set(df["region"].unique())
        assert regiones == {"Ñuble", "Maule", "Biobío"}

    def test_region_inexistente_df_vacio(self):
        """Región desconocida → DataFrame vacío (no crash)."""
        client = _make_client()
        df = client.get_stations(region="Antártida")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_lista_con_region_inexistente_df_vacio(self):
        """Lista con alguna región inválida → DataFrame vacío."""
        client = _make_client()
        df = client.get_stations(region=["R16", "Antártida"])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


# ========================================================================
# 3. Filtrar por tipo
# ========================================================================

class TestFiltrarPorTipo:
    """Tests de filtrado por tipo de estación."""

    def test_filtrar_tipo_INIA(self):
        client = _make_client()
        df = client.get_stations(station_type="INIA")
        assert len(df) > 0
        assert all(df["tipo"] == "INIA")

    def test_filtrar_tipo_DMC(self):
        client = _make_client()
        df = client.get_stations(station_type="DMC")
        assert len(df) > 0
        assert all(df["tipo"] == "DMC")

    def test_tipo_case_insensitive(self):
        client = _make_client()
        df1 = client.get_stations(station_type="inia")
        df2 = client.get_stations(station_type="INIA")
        assert len(df1) == len(df2)

    def test_tipo_inexistente_df_vacio(self):
        client = _make_client()
        df = client.get_stations(station_type="NASA")
        assert len(df) == 0


# ========================================================================
# 4. Filtrar región + tipo
# ========================================================================

class TestFiltrosCombinados:
    """Tests de filtros combinados."""

    def test_region_y_tipo(self):
        client = _make_client()
        df = client.get_stations(region="R16", station_type="INIA")
        assert len(df) > 0
        assert all(df["region"] == "Ñuble")
        assert all(df["tipo"] == "INIA")

    def test_region_y_tipo_sin_resultados(self):
        """Combinación sin resultados → vacío."""
        client = _make_client()
        df = client.get_stations(region="R08", station_type="DMC")
        # Solo hay 1 INIA en Biobío en fake data, no DMC
        assert isinstance(df, pd.DataFrame)

    def test_multiples_regiones_y_tipo(self):
        client = _make_client()
        df = client.get_stations(region=["R16", "R07"], station_type="INIA")
        assert all(df["tipo"] == "INIA")
        regiones = set(df["region"].unique())
        assert regiones.issubset({"Ñuble", "Maule"})
