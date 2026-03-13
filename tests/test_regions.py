"""
test_regions.py – Regiones: normalización, formatos, errores.

Cubre:
    - Código con R (R16, R08, R07)
    - Solo número (16, 8, 7)
    - Nombre completo (Ñuble, Biobío, Maule)
    - Nombre sin tildes (nuble, biobio)
    - Código en minúsculas (r16)
    - Lista de regiones
    - Región que no existe → ValueError
    - REGION_MAP completitud (16 regiones)
"""

import pytest

from iniamet.utils import (
    normalize_region,
    normalize_regions,
    get_region_code,
    get_region_name,
    REGION_MAP,
)


# ========================================================================
# 1. normalize_region (entrada única)
# ========================================================================

class TestNormalizeRegion:
    """Normalización de una sola región."""

    # --- Código R## ---
    @pytest.mark.parametrize("entrada,esperado", [
        ("R16", "Ñuble"),
        ("R08", "Biobío"),
        ("R07", "Maule"),
        ("R13", "Metropolitana"),
        ("R15", "Arica y Parinacota"),
    ])
    def test_codigo_R_valido(self, entrada, esperado):
        assert normalize_region(entrada) == esperado

    def test_codigo_R_minusculas(self):
        assert normalize_region("r16") == "Ñuble"
        assert normalize_region("r08") == "Biobío"

    # --- Solo número ---
    @pytest.mark.parametrize("entrada,esperado", [
        ("16", "Ñuble"),
        ("8", "Biobío"),
        ("08", "Biobío"),
        ("7", "Maule"),
        ("07", "Maule"),
        ("13", "Metropolitana"),
    ])
    def test_solo_numero(self, entrada, esperado):
        assert normalize_region(entrada) == esperado

    # --- Nombre completo ---
    @pytest.mark.parametrize("entrada,esperado", [
        ("Ñuble", "Ñuble"),
        ("Biobío", "Biobío"),
        ("Maule", "Maule"),
        ("Metropolitana", "Metropolitana"),
        ("Los Lagos", "Los Lagos"),
    ])
    def test_nombre_completo(self, entrada, esperado):
        assert normalize_region(entrada) == esperado

    # --- Nombre sin tildes / mayúsculas ---
    def test_nombre_sin_tildes(self):
        assert normalize_region("nuble") == "Ñuble"

    def test_nombre_mayusculas(self):
        assert normalize_region("MAULE") == "Maule"

    def test_nombre_biobio_sin_tilde(self):
        assert normalize_region("biobio") == "Biobío"

    # --- Errores ---
    def test_region_inexistente_falla(self):
        with pytest.raises(ValueError, match="Unknown region"):
            normalize_region("Antártida")

    def test_numero_invalido_falla(self):
        with pytest.raises(ValueError, match="Unknown region"):
            normalize_region("99")

    def test_string_vacio_falla(self):
        with pytest.raises(ValueError):
            normalize_region("")


# ========================================================================
# 2. normalize_regions (lista / str)
# ========================================================================

class TestNormalizeRegions:
    """Normalización para una o varias regiones."""

    def test_string_unico_retorna_lista(self):
        result = normalize_regions("R16")
        assert result == ["Ñuble"]
        assert isinstance(result, list)

    def test_lista_una_region(self):
        assert normalize_regions(["R16"]) == ["Ñuble"]

    def test_lista_dos_regiones(self):
        result = normalize_regions(["R16", "R08"])
        assert set(result) == {"Ñuble", "Biobío"}

    def test_lista_tres_regiones(self):
        result = normalize_regions(["R16", "R08", "R07"])
        assert set(result) == {"Ñuble", "Biobío", "Maule"}

    def test_lista_mixta_formatos(self):
        """Acepta mezcla de formatos: código, número, nombre."""
        result = normalize_regions(["R16", "8", "Maule"])
        assert set(result) == {"Ñuble", "Biobío", "Maule"}

    def test_lista_con_region_invalida_falla(self):
        """Si una región es inválida, ValueError."""
        with pytest.raises(ValueError):
            normalize_regions(["R16", "Antártida"])


# ========================================================================
# 3. get_region_code / get_region_name
# ========================================================================

class TestRegionCodeName:
    """Conversión código ↔ nombre."""

    def test_get_code_desde_nombre(self):
        assert get_region_code("Ñuble") == "R16"
        assert get_region_code("Biobío") == "R08"

    def test_get_code_desde_codigo(self):
        """Si ya es código, lo retorna normalizado."""
        assert get_region_code("R16") == "R16"

    def test_get_code_invalido(self):
        assert get_region_code("Antártida") is None

    def test_get_name_desde_codigo(self):
        assert get_region_name("R16") == "Ñuble"
        assert get_region_name("R07") == "Maule"


# ========================================================================
# 4. REGION_MAP
# ========================================================================

class TestRegionMap:
    """Mapa de regiones."""

    def test_16_regiones(self):
        """Chile tiene 16 regiones."""
        assert len(REGION_MAP) == 16

    def test_todas_empiezan_con_R(self):
        for code in REGION_MAP:
            assert code.startswith("R")

    def test_regiones_clave_existen(self):
        claves = {"R01", "R02", "R03", "R04", "R05", "R06", "R07",
                   "R08", "R09", "R10", "R11", "R12", "R13", "R14",
                   "R15", "R16"}
        assert set(REGION_MAP.keys()) == claves
