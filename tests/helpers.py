"""
helpers.py – Constantes y funciones de utilidad compartidas entre tests.

Separado de conftest.py para que los test files puedan importarlas
directamente sin depender del mecanismo especial de conftest de pytest.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Datos falsos que simulan respuestas de la API
# ---------------------------------------------------------------------------

FAKE_STATIONS = [
    {
        "identificador": "INIA-47",
        "nombre": "Ninhue",
        "region": "Ñuble",
        "comuna": "Chillán",
        "latitud": -36.41,
        "longitud": -72.40,
        "elevacion": 80,
        "primer_dato": "2010-01-01",
    },
    {
        "identificador": "INIA-139",
        "nombre": "Centro Experimental Arroz",
        "region": "Ñuble",
        "comuna": "San Carlos",
        "latitud": -36.62,
        "longitud": -71.95,
        "elevacion": 140,
        "primer_dato": "2012-06-01",
    },
    {
        "identificador": "INIA-351",
        "nombre": "Quilamapu",
        "region": "Ñuble",
        "comuna": "Chillán",
        "latitud": -36.59,
        "longitud": -72.09,
        "elevacion": 217,
        "primer_dato": "2015-01-01",
    },
    {
        "identificador": "DMC-360097",
        "nombre": "Liceo San Nicolás",
        "region": "Ñuble",
        "comuna": "San Nicolás",
        "latitud": -36.50,
        "longitud": -72.21,
        "elevacion": 120,
        "primer_dato": "2019-01-01",
    },
    {
        "identificador": "INIA-100",
        "nombre": "Cauquenes",
        "region": "Maule",
        "comuna": "Cauquenes",
        "latitud": -35.97,
        "longitud": -72.32,
        "elevacion": 177,
        "primer_dato": "2011-01-01",
    },
    {
        "identificador": "DMC-350028",
        "nombre": "Panguilemo",
        "region": "Maule",
        "comuna": "Talca",
        "latitud": -35.38,
        "longitud": -71.60,
        "elevacion": 100,
        "primer_dato": "2013-01-01",
    },
    {
        "identificador": "INIA-200",
        "nombre": "Nahuelbuta",
        "region": "Biobío",
        "comuna": "Los Ángeles",
        "latitud": -37.47,
        "longitud": -72.35,
        "elevacion": 150,
        "primer_dato": "2014-01-01",
    },
]

FAKE_VARIABLES_INIA47 = [
    {"identificador": 2002, "nombre": "Temperatura del Aire Media", "unidad": "Grados Celcius"},
    {"identificador": 2001, "nombre": "Precipitación", "unidad": "Milímetros"},
    {"identificador": 2007, "nombre": "Humedad Relativa Media", "unidad": "Porcentaje"},
    {"identificador": 2022, "nombre": "Radiación Media", "unidad": "Watts por metro cuadrado"},
    {"identificador": 2013, "nombre": "Velocidad Viento Media", "unidad": "Metros por Segundo"},
    {"identificador": 2125, "nombre": "Presión Atmosférica", "unidad": "milibares"},
]


def _make_fake_data(n=96, var_id=2002, start="2025-01-01"):
    """Genera n registros falsos cada 15 min."""
    rng = pd.date_range(start, periods=n, freq="15min")
    if var_id == 2001:  # precipitación
        valores = np.random.exponential(0.1, n).round(2)
    else:
        valores = (
            15 + 10 * np.sin(np.linspace(0, 2 * 3.14159, n)) +
            np.random.normal(0, 0.5, n)
        ).round(2)
    return [{"tiempo": t.isoformat(), "valor": str(v)} for t, v in zip(rng, valores)]
