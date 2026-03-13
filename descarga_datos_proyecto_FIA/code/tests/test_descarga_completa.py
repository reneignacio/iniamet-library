#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
TESTS PARA VALIDACIÓN DE DESCARGA COMPLETA - PROYECTO FIA
================================================================================

Tests para verificar:
1. Estructura de datos correcta
2. Cálculos lógicos (GDD, VPD, ETo, etc.)
3. Manejo de NAs
4. Consistencia entre agregaciones
5. Rangos físicos válidos
6. Redondeo correcto de valores

Ejecutar con: pytest tests/test_descarga_completa.py -v
================================================================================
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime

# Añadir path del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(SCRIPT_DIR)  # code/
PROJECT_DIR = os.path.dirname(CODE_DIR)  # descarga_datos_proyecto_FIA/
DATOS_DIR = os.path.join(PROJECT_DIR, 'datos')

sys.path.insert(0, CODE_DIR)

# ============================================================================
# CONFIGURACIÓN DE DECIMALES (misma que en script principal)
# ============================================================================
DECIMALES = {
    'default': 1,
    'vpd': 2,
    'eto': 2,
    'coordenadas': 6,
    'elevacion': 0,
}

# ============================================================================
# FUNCIONES A TESTEAR (copiadas del script principal)
# ============================================================================

def grados_a_cardinal(grados):
    """Convierte grados (0-360) a dirección cardinal."""
    if pd.isna(grados):
        return np.nan
    grados = grados % 360
    direcciones = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
    idx = int((grados + 22.5) / 45) % 8
    return direcciones[idx]


def calcular_vpd(temp, hr):
    """Déficit de Presión de Vapor (kPa)."""
    if pd.isna(temp) or pd.isna(hr):
        return np.nan
    es = 0.6108 * np.exp(17.27 * temp / (temp + 237.3))
    ea = es * (hr / 100)
    return round(max(0, es - ea), DECIMALES['vpd'])


def calcular_eto_hargreaves(tmin, tmax, tmean, lat, doy):
    """ETo Hargreaves (mm/día)."""
    if pd.isna(tmin) or pd.isna(tmax) or pd.isna(tmean):
        return np.nan
    lat_rad = np.radians(abs(lat))
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(lat_rad) * np.tan(delta), -1, 1))
    Ra = (24 * 60 / np.pi) * 0.082 * dr * (
        ws * np.sin(lat_rad) * np.sin(delta) +
        np.cos(lat_rad) * np.cos(delta) * np.sin(ws)
    )
    Ra_mm = Ra / 2.45
    eto = 0.0023 * (tmean + 17.8) * np.sqrt(max(0, tmax - tmin)) * Ra_mm
    return round(max(0, eto), DECIMALES['eto'])


def calcular_gdd(tmax, tmin, t_base=10):
    """Grados Día de Crecimiento."""
    if pd.isna(tmax) or pd.isna(tmin):
        return np.nan
    return round(max(0, (tmax + tmin) / 2 - t_base), DECIMALES['default'])


# ============================================================================
# TESTS DE CONVERSIÓN DE DIRECCIÓN DEL VIENTO
# ============================================================================

class TestDireccionViento:
    """Tests para conversión de grados a dirección cardinal."""

    def test_norte(self):
        """0° y 360° deben ser Norte."""
        assert grados_a_cardinal(0) == 'N'
        assert grados_a_cardinal(360) == 'N'
        assert grados_a_cardinal(10) == 'N'
        assert grados_a_cardinal(350) == 'N'

    def test_direcciones_cardinales(self):
        """Verificar direcciones principales."""
        assert grados_a_cardinal(45) == 'NE'
        assert grados_a_cardinal(90) == 'E'
        assert grados_a_cardinal(135) == 'SE'
        assert grados_a_cardinal(180) == 'S'
        assert grados_a_cardinal(225) == 'SO'
        assert grados_a_cardinal(270) == 'O'
        assert grados_a_cardinal(315) == 'NO'

    def test_limites_direcciones(self):
        """Verificar límites entre direcciones (22.5° cada una)."""
        # Límite N-NE es 22.5°
        assert grados_a_cardinal(22) == 'N'
        assert grados_a_cardinal(23) == 'NE'
        # Límite NE-E es 67.5°
        assert grados_a_cardinal(67) == 'NE'
        assert grados_a_cardinal(68) == 'E'

    def test_na_handling(self):
        """NaN debe retornar NaN."""
        assert pd.isna(grados_a_cardinal(np.nan))
        assert pd.isna(grados_a_cardinal(None))

    def test_valores_mayores_360(self):
        """Valores > 360 deben normalizar."""
        assert grados_a_cardinal(450) == 'E'  # 450 % 360 = 90
        assert grados_a_cardinal(720) == 'N'  # 720 % 360 = 0


# ============================================================================
# TESTS DE VPD (Déficit de Presión de Vapor)
# ============================================================================

class TestVPD:
    """Tests para cálculo de VPD."""

    def test_vpd_basico(self):
        """VPD con valores típicos."""
        # A 20°C y 50% HR, VPD debe ser ~1.17 kPa
        vpd = calcular_vpd(20, 50)
        assert 1.0 < vpd < 1.3

    def test_vpd_saturado(self):
        """VPD con 100% HR debe ser ~0."""
        vpd = calcular_vpd(20, 100)
        assert vpd < 0.01

    def test_vpd_seco(self):
        """VPD con baja HR debe ser alto."""
        vpd = calcular_vpd(30, 20)
        assert vpd > 3.0

    def test_vpd_no_negativo(self):
        """VPD nunca debe ser negativo."""
        for temp in range(-10, 45, 5):
            for hr in range(0, 101, 10):
                vpd = calcular_vpd(temp, max(hr, 1))  # Evitar HR=0 exacto
                assert vpd >= 0 or pd.isna(vpd)

    def test_vpd_na_handling(self):
        """NaN en entrada debe retornar NaN."""
        assert pd.isna(calcular_vpd(np.nan, 50))
        assert pd.isna(calcular_vpd(20, np.nan))
        assert pd.isna(calcular_vpd(np.nan, np.nan))

    def test_vpd_rango_fisico(self):
        """VPD debe estar en rango físicamente posible (0-10 kPa)."""
        vpd = calcular_vpd(40, 10)  # Condiciones extremas
        assert 0 <= vpd <= 10

    def test_vpd_decimales(self):
        """VPD debe tener 2 decimales."""
        vpd = calcular_vpd(20, 50)
        vpd_str = f"{vpd:.10f}"
        # Verificar que tiene máximo 2 decimales significativos
        assert vpd == round(vpd, 2)


# ============================================================================
# TESTS DE GDD (Grados Día de Crecimiento)
# ============================================================================

class TestGDD:
    """Tests para cálculo de GDD."""

    def test_gdd_basico(self):
        """GDD con valores típicos."""
        # Tmax=25, Tmin=15, base=10 -> (25+15)/2 - 10 = 10
        gdd = calcular_gdd(25, 15, 10)
        assert gdd == 10.0

    def test_gdd_bajo_base(self):
        """GDD cuando temperatura < base debe ser 0."""
        gdd = calcular_gdd(8, 2, 10)  # Media = 5 < 10
        assert gdd == 0.0

    def test_gdd_no_negativo(self):
        """GDD nunca debe ser negativo."""
        gdd = calcular_gdd(-5, -10, 10)
        assert gdd == 0.0

    def test_gdd_na_handling(self):
        """NaN en entrada debe retornar NaN."""
        assert pd.isna(calcular_gdd(np.nan, 15, 10))
        assert pd.isna(calcular_gdd(25, np.nan, 10))

    def test_gdd_acumulacion(self):
        """Verificar que GDD se acumula correctamente."""
        dias = [
            (25, 15),  # GDD = 10
            (30, 20),  # GDD = 15
            (20, 10),  # GDD = 5
        ]
        total = sum(calcular_gdd(tmax, tmin, 10) for tmax, tmin in dias)
        assert total == 30.0

    def test_gdd_decimales(self):
        """GDD debe tener 1 decimal."""
        gdd = calcular_gdd(27, 13, 10)
        assert gdd == round(gdd, 1)


# ============================================================================
# TESTS DE ETo HARGREAVES
# ============================================================================

class TestETo:
    """Tests para cálculo de ETo Hargreaves."""

    def test_eto_basico(self):
        """ETo con valores típicos debe estar en rango razonable."""
        # Verano en Chile central (lat -35, día 180)
        eto = calcular_eto_hargreaves(15, 30, 22.5, -35, 180)
        assert 2 < eto < 8  # Rango típico verano

    def test_eto_invierno(self):
        """ETo en invierno debe ser menor."""
        eto_verano = calcular_eto_hargreaves(15, 30, 22.5, -35, 180)
        eto_invierno = calcular_eto_hargreaves(5, 15, 10, -35, 180)
        assert eto_invierno < eto_verano

    def test_eto_no_negativo(self):
        """ETo nunca debe ser negativo."""
        for tmin in range(-5, 20, 5):
            for tmax in range(tmin + 5, 40, 5):
                tmean = (tmin + tmax) / 2
                eto = calcular_eto_hargreaves(tmin, tmax, tmean, -35, 180)
                assert eto >= 0 or pd.isna(eto)

    def test_eto_na_handling(self):
        """NaN en entrada debe retornar NaN."""
        assert pd.isna(calcular_eto_hargreaves(np.nan, 30, 22.5, -35, 180))
        assert pd.isna(calcular_eto_hargreaves(15, np.nan, 22.5, -35, 180))
        assert pd.isna(calcular_eto_hargreaves(15, 30, np.nan, -35, 180))

    def test_eto_rango_fisico(self):
        """ETo debe estar en rango físicamente posible (0-15 mm/día)."""
        eto = calcular_eto_hargreaves(20, 40, 30, -35, 180)
        assert 0 <= eto <= 15

    def test_eto_decimales(self):
        """ETo debe tener 2 decimales."""
        eto = calcular_eto_hargreaves(15, 30, 22.5, -35, 180)
        assert eto == round(eto, 2)


# ============================================================================
# TESTS DE VALIDACIÓN DE ARCHIVOS GENERADOS
# ============================================================================

class TestArchivosGenerados:
    """Tests para validar archivos CSV generados."""

    @pytest.fixture
    def base_dir(self):
        """Directorio base de datos."""
        return DATOS_DIR

    def test_estructura_carpetas(self, base_dir):
        """Verificar que existen las carpetas esperadas."""
        carpetas = ['raw', 'horario', 'diario', 'indices']
        for carpeta in carpetas:
            path = os.path.join(base_dir, carpeta)
            if os.path.exists(base_dir):
                assert os.path.exists(path), f"Falta carpeta: {carpeta}"

    def test_columnas_raw(self, base_dir):
        """Verificar columnas en archivos raw."""
        raw_dir = os.path.join(base_dir, 'raw')
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(raw_dir, files[0]))
                # Columnas obligatorias
                required = ['estacion_codigo', 'estacion_nombre', 'region', 'tiempo']
                for col in required:
                    assert col in df.columns, f"Falta columna: {col}"

    def test_columnas_indices(self, base_dir):
        """Verificar columnas en archivos de índices."""
        indices_dir = os.path.join(base_dir, 'indices')
        if os.path.exists(indices_dir):
            files = [f for f in os.listdir(indices_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(indices_dir, files[0]))
                # Columnas de índices
                expected = ['fecha', 'GDD', 'GDD_acum', 'VPD_kPa', 'ETo_mm']
                for col in expected:
                    assert col in df.columns, f"Falta columna de índice: {col}"

    def test_valores_fisicos_temperatura(self, base_dir):
        """Verificar que temperaturas están en rango físico."""
        raw_dir = os.path.join(base_dir, 'raw')
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(raw_dir, files[0]))
                temp_cols = [c for c in df.columns if 'temperatura' in c.lower()]
                for col in temp_cols:
                    # Temperatura entre -40 y 60 °C
                    valid = df[col].dropna()
                    if len(valid) > 0:
                        assert valid.min() > -40, f"Temperatura muy baja en {col}"
                        assert valid.max() < 60, f"Temperatura muy alta en {col}"

    def test_valores_fisicos_humedad(self, base_dir):
        """Verificar que humedad está en rango 0-100%."""
        raw_dir = os.path.join(base_dir, 'raw')
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(raw_dir, files[0]))
                hr_cols = [c for c in df.columns if 'humedad' in c.lower()]
                for col in hr_cols:
                    valid = df[col].dropna()
                    if len(valid) > 0:
                        assert valid.min() >= 0, f"Humedad negativa en {col}"
                        assert valid.max() <= 100, f"Humedad > 100% en {col}"

    def test_direccion_cardinal_valida(self, base_dir):
        """Verificar que direcciones cardinales son válidas."""
        raw_dir = os.path.join(base_dir, 'raw')
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(raw_dir, files[0]))
                cardinal_cols = [c for c in df.columns if 'cardinal' in c.lower()]
                valid_directions = {'N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'}
                for col in cardinal_cols:
                    unique = set(df[col].dropna().unique())
                    assert unique.issubset(valid_directions), f"Direcciones inválidas en {col}: {unique - valid_directions}"

    def test_valores_redondeados(self, base_dir):
        """Verificar que valores numéricos están redondeados correctamente."""
        raw_dir = os.path.join(base_dir, 'raw')
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
            if files:
                df = pd.read_csv(os.path.join(raw_dir, files[0]))
                # Verificar que temperatura tiene 1 decimal
                temp_cols = [c for c in df.columns if 'temperatura' in c.lower()]
                for col in temp_cols:
                    valid = df[col].dropna()
                    if len(valid) > 0:
                        # Verificar que todos los valores tienen máximo 1 decimal
                        decimals = valid.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                        assert decimals.max() <= 1, f"Demasiados decimales en {col}"


# ============================================================================
# TESTS DE CONSISTENCIA ENTRE AGREGACIONES
# ============================================================================

class TestConsistenciaAgregaciones:
    """Tests para verificar consistencia entre niveles de agregación."""

    @pytest.fixture
    def sample_data(self):
        """Crear datos de prueba."""
        np.random.seed(42)
        n = 96 * 7  # 7 días de datos cada 15 min

        dates = pd.date_range('2024-01-01', periods=n, freq='15min')
        df = pd.DataFrame({
            'tiempo': dates,
            'temperatura': np.random.normal(20, 5, n),
            'precipitacion': np.abs(np.random.normal(0, 0.5, n)),
            'humedad': np.clip(np.random.normal(60, 15, n), 0, 100)
        })
        return df

    def test_agregacion_horaria_count(self, sample_data):
        """Verificar que agregación horaria tiene 4 veces menos filas."""
        df = sample_data.copy()
        df = df.set_index('tiempo')
        df_hourly = df.resample('h').mean()

        # 96 registros/día * 7 días = 672 raw
        # 24 horas/día * 7 días = 168 horario
        expected_ratio = 4  # 96/24
        actual_ratio = len(sample_data) / len(df_hourly)
        assert abs(actual_ratio - expected_ratio) < 0.1

    def test_agregacion_diaria_count(self, sample_data):
        """Verificar que agregación diaria tiene días correctos."""
        df = sample_data.copy()
        df = df.set_index('tiempo')
        df_daily = df.resample('D').mean()

        # Debe haber 7 días
        assert len(df_daily) == 7

    def test_precipitacion_suma_vs_media(self, sample_data):
        """Precipitación diaria debe ser suma, no media."""
        df = sample_data.copy()
        df = df.set_index('tiempo')

        precip_sum = df['precipitacion'].resample('D').sum()
        precip_mean = df['precipitacion'].resample('D').mean()

        # Suma debe ser ~96 veces la media (96 registros por día)
        ratio = precip_sum.mean() / precip_mean.mean()
        assert 90 < ratio < 100

    def test_temperatura_min_max_media(self, sample_data):
        """Verificar relación min <= media <= max en agregación diaria."""
        df = sample_data.copy()
        df = df.set_index('tiempo')

        t_min = df['temperatura'].resample('D').min()
        t_mean = df['temperatura'].resample('D').mean()
        t_max = df['temperatura'].resample('D').max()

        for i in range(len(t_min)):
            assert t_min.iloc[i] <= t_mean.iloc[i] <= t_max.iloc[i]


# ============================================================================
# TESTS DE MANEJO DE NAs
# ============================================================================

class TestManejoNAs:
    """Tests para verificar manejo correcto de valores faltantes."""

    def test_na_en_calculos_no_propaga_errores(self):
        """Funciones deben manejar NAs sin errores."""
        # No debe lanzar excepción
        grados_a_cardinal(np.nan)
        calcular_vpd(np.nan, 50)
        calcular_gdd(np.nan, 15)
        calcular_eto_hargreaves(np.nan, 30, 22, -35, 180)

    def test_dataframe_con_nas(self):
        """DataFrame con NAs debe procesarse sin errores."""
        df = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=10, freq='D'),
            'temp': [20, np.nan, 22, 23, np.nan, 25, 26, np.nan, 28, 29],
            'hr': [50, 55, np.nan, 60, 65, np.nan, 70, 75, 80, np.nan]
        })

        # Calcular VPD con NAs
        df['vpd'] = df.apply(lambda r: calcular_vpd(r['temp'], r['hr']), axis=1)

        # Debe haber NAs donde falta temp O hr
        assert df['vpd'].isna().sum() >= 3  # Al menos donde falta temp o hr


# ============================================================================
# FUNCIÓN PARA EJECUTAR VALIDACIÓN COMPLETA
# ============================================================================

def validar_datos_completos(base_dir=None):
    """
    Ejecuta validación completa de todos los datos generados.

    Retorna dict con resultados y estadísticas.
    """
    if base_dir is None:
        base_dir = DATOS_DIR

    resultados = {
        'errores': [],
        'warnings': [],
        'estadisticas': {}
    }

    carpetas = ['raw', 'horario', 'diario', 'indices']

    for carpeta in carpetas:
        path = os.path.join(base_dir, carpeta)
        if not os.path.exists(path):
            resultados['errores'].append(f"Carpeta no existe: {carpeta}")
            continue

        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        resultados['estadisticas'][carpeta] = {
            'archivos': len(files),
            'filas_total': 0,
            'nas_por_variable': {}
        }

        for file in files:
            try:
                df = pd.read_csv(os.path.join(path, file))
                resultados['estadisticas'][carpeta]['filas_total'] += len(df)

                # Contar NAs por variable
                for col in df.columns:
                    na_count = df[col].isna().sum()
                    na_pct = na_count / len(df) * 100

                    if col not in resultados['estadisticas'][carpeta]['nas_por_variable']:
                        resultados['estadisticas'][carpeta]['nas_por_variable'][col] = []

                    resultados['estadisticas'][carpeta]['nas_por_variable'][col].append(na_pct)

                    # Warning si > 10% NAs
                    if na_pct > 10:
                        resultados['warnings'].append(
                            f"{file}/{col}: {na_pct:.1f}% NAs"
                        )

            except Exception as e:
                resultados['errores'].append(f"Error leyendo {file}: {e}")

    return resultados


if __name__ == '__main__':
    # Ejecutar tests
    pytest.main([__file__, '-v', '--tb=short'])

    # Ejecutar validación adicional
    print("\n" + "="*70)
    print("VALIDACIÓN COMPLETA DE DATOS - PROYECTO FIA")
    print("="*70)

    resultados = validar_datos_completos()

    print(f"\nErrores: {len(resultados['errores'])}")
    for error in resultados['errores'][:5]:
        print(f"  - {error}")

    print(f"\nWarnings: {len(resultados['warnings'])}")
    for warning in resultados['warnings'][:5]:
        print(f"  - {warning}")

    print("\nEstadísticas por carpeta:")
    for carpeta, stats in resultados['estadisticas'].items():
        print(f"  {carpeta}/: {stats['archivos']} archivos, {stats['filas_total']:,} filas totales")
