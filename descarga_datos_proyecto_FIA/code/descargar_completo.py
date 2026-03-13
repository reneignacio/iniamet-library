#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
DESCARGA COMPLETA DE DATOS METEOROLÓGICOS INIA - ÑUBLE Y MAULE
Proyecto FIA
================================================================================

Estructura de salida:
descarga_datos_proyecto_FIA/
├── code/                     → Este script y tests
│   └── tests/
├── datos/
│   ├── raw/
│   │   ├── csv/              → Datos originales 15 min (CSV)
│   │   └── excel/            → Datos originales 15 min (Excel)
│   ├── horario/
│   │   ├── csv/              → Agregado horario (CSV)
│   │   └── excel/            → Agregado horario (Excel)
│   ├── diario/
│   │   ├── csv/              → Agregado diario (CSV)
│   │   └── excel/            → Agregado diario (Excel)
│   └── indices/
│       ├── csv/              → Índices agroclimáticos (CSV)
│       └── excel/            → Índices agroclimáticos (Excel)
└── geopackage/               → GeoPackage de estaciones

Orden de columnas:
1. FechaHora (UTC-4) o Fecha (UTC-4)
2. Variables: velocidad viento, vmax, dirección, presión, precipitación,
   radiación, temperatura, humedad

Características:
- Sin columnas de metadatos de estación en los archivos de datos
- Información de estaciones en Excel/GeoPackage separado (geopackage/)
- Valores redondeados a 1 decimal (2 para VPD, ETo)
- Dirección del viento en grados Y formato cardinal (N, NE, E, SE, S, SO, O, NO)
- Índices: GDD, Horas Frío, VPD, ETo (Hargreaves)
- Exportación dual: CSV y Excel
================================================================================
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

# Añadir el directorio src al path para importar iniamet
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from iniamet import INIAClient, normalize_regions
import pvlib
from pvlib.location import Location

# Suprimir warnings de pandas sobre frecuencias deprecadas
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*deprecated.*')
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
API_KEY = "6c66ed32deb984ce0fb41ffdc54c1e98b517fa50"

# Rutas relativas desde el script (code/) hacia datos/ y geopackage/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # descarga_datos_proyecto_FIA/
DATOS_DIR = os.path.join(PROJECT_DIR, 'datos')
GEOPACKAGE_DIR = os.path.join(PROJECT_DIR, 'geopackage')

REGIONES = ["16", "7"]  # Acepta: "16", "R16", "Ñuble", etc.
TEMP_BASE_GDD = 10      # Base para GDD
TEMP_FRIO = 7           # Umbral horas frío

# Decimales para redondeo según tipo de variable
DECIMALES = {
    'default': 1,           # Por defecto: 1 decimal
    'vpd': 1,               # VPD en kPa: 1 decimal
    'eto': 1,               # ETo en mm: 1 decimal
    'coordenadas': 6,       # Lat/Lon: 6 decimales
    'elevacion': 0,         # Elevación: sin decimales
}

DIRS = {
    'raw_csv': os.path.join(DATOS_DIR, 'raw', 'csv'),
    'raw_excel': os.path.join(DATOS_DIR, 'raw', 'excel'),
    'horario_csv': os.path.join(DATOS_DIR, 'horario', 'csv'),
    'horario_excel': os.path.join(DATOS_DIR, 'horario', 'excel'),
    'diario_csv': os.path.join(DATOS_DIR, 'diario', 'csv'),
    'diario_excel': os.path.join(DATOS_DIR, 'diario', 'excel'),
    'indices_csv': os.path.join(DATOS_DIR, 'indices', 'csv'),
    'indices_excel': os.path.join(DATOS_DIR, 'indices', 'excel')
}

# Directorio de caché (dentro del proyecto)
CACHE_DIR = os.path.join(PROJECT_DIR, 'cache')
STATIONS_CACHE_FILE = os.path.join(CACHE_DIR, 'stations', 'all_stations.json')

# Límite opcional para pruebas rápidas (0 = sin límite)
MAX_ESTACIONES = int(os.getenv('MAX_ESTACIONES', '0') or '0')

# Cliente INIA global (se inicializa en main)
inia_client = None

# ============================================================================
# FUNCIONES API (usando librería iniamet con caché)
# ============================================================================

def init_client():
    """Inicializa el cliente INIA con caché."""
    global inia_client
    inia_client = INIAClient(api_key=API_KEY, cache=True, cache_dir=CACHE_DIR)
    print(f"Cache habilitado en: {CACHE_DIR}")

def get_stations():
    """Obtiene todas las estaciones (con caché)."""
    df = inia_client.get_stations()
    # Renombrar columnas para compatibilidad
    if 'codigo' in df.columns:
        df = df.rename(columns={'codigo': 'identificador'})
    return df

def get_variables(station_code):
    """Variables disponibles para una estación (con caché)."""
    try:
        df = inia_client.get_variables(station_code)
        # Renombrar columnas para compatibilidad
        if 'variable_id' in df.columns:
            df = df.rename(columns={'variable_id': 'identificador'})
        return df
    except Exception as e:
        print(f"  Error obteniendo variables: {e}")
        return pd.DataFrame()

def get_data(station, variable, start_date, end_date):
    """Descarga datos de una variable (con caché)."""
    try:
        df = inia_client.get_data(
            station=station,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        return df
    except Exception as e:
        print(f"  Error descargando datos: {e}")
        return pd.DataFrame()


def cargar_ubicaciones_estaciones(filepath=STATIONS_CACHE_FILE):
    """Carga ubicaciones por código desde all_stations.json."""
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo de ubicaciones no encontrado: {filepath}")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rows = json.load(f)

        ubicaciones = {}
        for row in rows:
            code = str(row.get('codigo', '')).strip()
            if code:
                ubicaciones[code] = row

        print(f"Ubicaciones cargadas: {len(ubicaciones):,} desde cache/stations/all_stations.json")
        return ubicaciones
    except Exception as e:
        print(f"⚠️ Error leyendo ubicaciones de estaciones: {e}")
        return {}


def _to_float_or_default(value, default):
    """Convierte a float con fallback seguro."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def resolver_metadatos_estacion(station, ubicaciones):
    """Resuelve lat/lon/elev/primer con prioridad en archivo de ubicaciones."""
    code = str(station.get('identificador', '')).strip()
    ref = ubicaciones.get(code, {})

    lat = _to_float_or_default(ref.get('latitud', station.get('latitud', -35)), -35.0)
    lon = _to_float_or_default(ref.get('longitud', station.get('longitud', -71)), -71.0)
    elev = _to_float_or_default(ref.get('elevacion', station.get('elevacion', 0)), 0.0)
    primer = ref.get('primera_lectura', station.get('primera_lectura', '2015-01-01'))

    return lat, lon, elev, primer

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def grados_a_cardinal(grados):
    """Convierte grados (0-360) a dirección cardinal (N, NE, E, etc.)."""
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

def redondear_dataframe(df, decimales=1):
    """Redondea todas las columnas numéricas de un DataFrame."""
    df_rounded = df.copy()
    for col in df_rounded.select_dtypes(include=[np.number]).columns:
        # Coordenadas: más decimales
        if col in ['latitud', 'longitud']:
            df_rounded[col] = df_rounded[col].round(DECIMALES['coordenadas'])
        # Elevación: sin decimales
        elif col == 'elevacion':
            df_rounded[col] = df_rounded[col].round(DECIMALES['elevacion'])
        # VPD: 2 decimales
        elif 'vpd' in col.lower():
            df_rounded[col] = df_rounded[col].round(DECIMALES['vpd'])
        # ETo: 2 decimales
        elif 'eto' in col.lower():
            df_rounded[col] = df_rounded[col].round(DECIMALES['eto'])
        # Resto: 1 decimal
        else:
            df_rounded[col] = df_rounded[col].round(decimales)
    return df_rounded

def ordenar_columnas(df, es_diario=False):
    """
    Reordena las columnas del DataFrame según especificación:
    1. FechaHora (UTC-4) o Fecha (UTC-4)
    2. Variables en orden: viento, vmax, dirección, presión, precipitación, radiación, temperatura, humedad
    También renombra columnas a nombres más cortos.
    NO incluye columnas de metadata (código, nombre, región, coordenadas).
    """
    df = df.copy()

    # Eliminar columnas de metadatos si existen (no deben estar en archivos de datos)
    meta_cols = ['estacion_codigo', 'estacion_nombre', 'region', 'latitud', 'longitud', 'elevacion']
    df = df.drop(columns=[c for c in meta_cols if c in df.columns], errors='ignore')

    # Renombrar columna de tiempo
    if 'tiempo' in df.columns:
        df = df.rename(columns={'tiempo': 'FechaHora (UTC-4)'})
    if 'fecha' in df.columns:
        df = df.rename(columns={'fecha': 'Fecha (UTC-4)'})

    # Columna de fecha/tiempo
    fecha_col = 'FechaHora (UTC-4)' if 'FechaHora (UTC-4)' in df.columns else 'Fecha (UTC-4)'

    # Obtener todas las columnas de variables (metadata ya fue eliminada)
    todas_cols = list(df.columns)
    cols_restantes = [c for c in todas_cols if c != fecha_col]

    # Clasificar columnas por tipo de variable
    def prioridad_columna(col):
        col_lower = col.lower()
        # Velocidad del viento (media primero)
        if ('velocidad' in col_lower and 'viento' in col_lower) or col_lower.startswith('velocidad_viento'):
            if 'max' in col_lower or 'máx' in col_lower:
                return 2  # Vmax después de velocidad media
            return 1
        # Dirección del viento
        if 'direcci' in col_lower and 'viento' in col_lower:
            if 'cardinal' in col_lower:
                return 4  # Cardinal después de grados
            return 3
        # Presión atmosférica
        if 'presi' in col_lower and 'atmosf' in col_lower:
            return 5
        # Precipitación
        if 'precipit' in col_lower:
            return 6
        # Radiación
        if 'radiaci' in col_lower:
            return 7
        # Nubosidad (justo después de radiación)
        if 'nubosidad' in col_lower:
            return 7.5
        # Día/Noche (junto a radiación)
        if 'dia_noche' in col_lower or 'periodo_dia_noche' in col_lower:
            return 7.6
        # Temperatura
        if 'temperatura' in col_lower or 'temp_' in col_lower:
            return 8
        # Humedad
        if 'humedad' in col_lower:
            return 9
        # Resto al final
        return 10

    # Ordenar columnas de variables
    cols_ordenadas = sorted(cols_restantes, key=prioridad_columna)

    # Construir orden final: fecha primero, luego variables ordenadas
    orden_final = []
    if fecha_col in df.columns:
        orden_final.append(fecha_col)
    orden_final.extend(cols_ordenadas)

    df = df[orden_final]

    # Renombrar columnas a nombres más cortos
    renombres = {
        'FechaHora (UTC-4)': 'FechaHora_UTC4',
        'Fecha (UTC-4)': 'Fecha_UTC4',
        'Velocidad_Viento_Media': 'VV',
        'Velocidad_Viento_Máxima': 'VV_Max',
        'Dirección_del_Viento': 'Dir',
        'Dirección_del_Viento_cardinal': 'Dir_Card',
        'Presión_Atmosférica': 'Pres',
        'Precipitación': 'PP',
        'Radiación_Media': 'Rad',
        'Temperatura_del_Aire_Media': 'T',
        'Humedad_Relativa_Media': 'HR',
        # Para datos diarios
        'Temperatura_del_Aire_Media_min': 'T_Min',
        'Temperatura_del_Aire_Media_max': 'T_Max',
        'Temperatura_del_Aire_Media_media': 'T_Media',
        'Velocidad_Viento_Media_media': 'VV_Media',
        'Velocidad_Viento_Media_max': 'VV_Max',
        'Velocidad_Viento_Máxima_media': 'VV_Max_Media',
        'Velocidad_Viento_Máxima_max': 'VV_Max_Max',
        'Dirección_del_Viento_media': 'Dir_Media',
        'Presión_Atmosférica_media': 'Pres_Media',
        'Precipitación_acum': 'PP_Acum',
        'Radiación_Media_media': 'Rad_Media',
        'Nubosidad_pct': 'Nub',
        'Nubosidad_desc': 'Nub_Desc',
        'Nubosidad_pct_media': 'Nub_Media',
        'Dia_Noche': 'DiaNoche',
        'Dia_Noche_bin': 'DiaNoche_bin',
        'Periodo_Dia_Noche': 'DiaNoche',
        'Periodo_Dia_Noche_bin': 'DiaNoche_bin',
        'Humedad_Relativa_Media_media': 'HR_Media',
        # Para índices
        'VPD_kPa': 'VPD',
        'ETo_mm': 'ETo',
    }

    # Aplicar renombres que existan
    cols_actuales = df.columns.tolist()
    renombres_aplicar = {k: v for k, v in renombres.items() if k in cols_actuales}
    df = df.rename(columns=renombres_aplicar)

    # Agregar columna vacía para probabilidad
    df['Probabilidad (1-5)'] = np.nan

    return df

# ============================================================================
# NUBOSIDAD (Kasten-Czeplak invertida + pvlib cielo despejado)
# ============================================================================

# Coeficientes Kasten-Czeplak
COEF_A = 0.75   # coeficiente de atenuación promedio
COEF_B = 3.4    # exponente potencial
ELEVACION_SOLAR_MIN = 5.0   # grados mínimos de elevación solar
GHI_CLEAR_MIN = 50.0        # W/m² mínimo de cielo despejado

def calcular_nubosidad_horaria(df_h, lat, lon, elev, col_rad='Radiación_Media', col_tiempo='tiempo'):
    """
    Calcula nubosidad (%) a partir de radiación horaria usando Kasten-Czeplak invertida.

    Metodología:
      1. Modelo cielo despejado: Ineichen-Perez (pvlib)
      2. Índice de cielo despejado: Kc = GHI_medida / GHI_cielo_despejado
      3. Nubosidad: 100 × [(1 - Kc) / 0.75]^(1/3.4)

    Parámetros:
      df_h: DataFrame con datos horarios
      lat, lon, elev: coordenadas de la estación
      col_rad: nombre de la columna de radiación (W/m²)
      col_tiempo: nombre de la columna de tiempo
    """
    if col_rad not in df_h.columns:
        return df_h

    data = df_h.copy()
    data[col_tiempo] = pd.to_datetime(data[col_tiempo])

    # Crear índice temporal con timezone para pvlib
    idx = pd.DatetimeIndex(data[col_tiempo]).tz_localize('Etc/GMT+4')

    sitio = Location(latitude=lat, longitude=lon, tz='Etc/GMT+4', altitude=elev)

    # Posición solar y cielo despejado
    solar_pos = sitio.get_solarposition(idx)
    clearsky = sitio.get_clearsky(idx, model='ineichen')

    elevacion_solar = solar_pos['apparent_elevation'].values
    ghi_clear = clearsky['ghi'].values
    rad_medida = data[col_rad].values

    # Calcular Kc solo de día con suficiente radiación teórica
    es_dia = (elevacion_solar >= ELEVACION_SOLAR_MIN) & (ghi_clear >= GHI_CLEAR_MIN)
    data['Dia_Noche_bin'] = es_dia.astype(int)
    data['Dia_Noche'] = np.where(es_dia, 'Dia', 'Noche')

    nubosidad = np.full(len(data), np.nan)
    kc = np.where(es_dia, rad_medida / np.where(ghi_clear > 0, ghi_clear, 1), np.nan)
    kc = np.clip(kc, 0, 1.2)

    # Kc >= 1 → cielo despejado (0%)
    mask_despejado = es_dia & (kc >= 1.0)
    nubosidad[mask_despejado] = 0.0

    # Kc < 1 → Kasten-Czeplak invertida
    mask_nublado = es_dia & (kc < 1.0) & ~np.isnan(kc)
    ratio = np.clip((1.0 - kc[mask_nublado]) / COEF_A, 0, 1)
    nubosidad[mask_nublado] = 100.0 * np.power(ratio, 1.0 / COEF_B)
    nubosidad = np.clip(nubosidad, 0, 100)

    data['Nubosidad_pct'] = np.round(nubosidad, 1)

    # Etiqueta simple para facilitar lectura: categoria + porcentaje
    data['Nubosidad_desc'] = 'Noche'
    mask_nub_valida = data['Nubosidad_pct'].notna()
    mask_despejado = mask_nub_valida & (data['Nubosidad_pct'] <= 20)
    mask_parcial = mask_nub_valida & (data['Nubosidad_pct'] > 20) & (data['Nubosidad_pct'] <= 50)
    mask_nublado = mask_nub_valida & (data['Nubosidad_pct'] > 50) & (data['Nubosidad_pct'] <= 80)
    mask_cubierto = mask_nub_valida & (data['Nubosidad_pct'] > 80)

    data.loc[mask_despejado, 'Nubosidad_desc'] = 'Mayormente despejado'
    data.loc[mask_parcial, 'Nubosidad_desc'] = 'Parcialmente nublado'
    data.loc[mask_nublado, 'Nubosidad_desc'] = 'Nublado'
    data.loc[mask_cubierto, 'Nubosidad_desc'] = 'Cubierto'
    data.loc[mask_nub_valida, 'Nubosidad_desc'] = (
        data.loc[mask_nub_valida, 'Nubosidad_desc'] +
        ' (' + data.loc[mask_nub_valida, 'Nubosidad_pct'].round(0).astype(int).astype(str) + '%)'
    )

    return data


# ============================================================================
# FUNCIONES DE AGREGACIÓN
# ============================================================================

def agregar_horario(df_raw):
    """Agrega datos a resolución horaria."""
    if df_raw.empty:
        return df_raw
    df = df_raw.copy()
    df['tiempo'] = pd.to_datetime(df['tiempo'])
    meta_cols = ['estacion_codigo', 'estacion_nombre', 'region', 'latitud', 'longitud', 'elevacion']
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in meta_cols]

    df_grouped = df.set_index('tiempo')
    df_agg = df_grouped[numeric_cols].resample('h').mean()

    # Precipitación: sumar
    precip_cols = [c for c in numeric_cols if 'precipit' in c.lower()]
    for col in precip_cols:
        df_agg[col] = df_grouped[col].resample('h').sum()

    df_agg = df_agg.reset_index()
    for col in meta_cols:
        if col in df_raw.columns:
            df_agg[col] = df_raw[col].iloc[0]

    return redondear_dataframe(df_agg)

def agregar_diario(df_raw):
    """Agrega datos a resolución diaria con min/max/media."""
    if df_raw.empty:
        return df_raw
    df = df_raw.copy()
    df['tiempo'] = pd.to_datetime(df['tiempo'])
    meta_cols = ['estacion_codigo', 'estacion_nombre', 'region', 'latitud', 'longitud', 'elevacion']
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in meta_cols]

    df_grouped = df.set_index('tiempo')
    df_agg = pd.DataFrame()
    df_agg['fecha'] = df_grouped[numeric_cols[0]].resample('D').mean().index

    for col in numeric_cols:
        if 'temperatura' in col.lower() or 'temp' in col.lower():
            df_agg[f'{col}_min'] = df_grouped[col].resample('D').min().values
            df_agg[f'{col}_max'] = df_grouped[col].resample('D').max().values
            df_agg[f'{col}_media'] = df_grouped[col].resample('D').mean().values
        elif 'precipit' in col.lower():
            df_agg[f'{col}_acum'] = df_grouped[col].resample('D').sum().values
        elif 'viento' in col.lower() and 'direccion' not in col.lower():
            df_agg[f'{col}_media'] = df_grouped[col].resample('D').mean().values
            df_agg[f'{col}_max'] = df_grouped[col].resample('D').max().values
        else:
            df_agg[f'{col}_media'] = df_grouped[col].resample('D').mean().values

    for col in meta_cols:
        if col in df_raw.columns:
            df_agg[col] = df_raw[col].iloc[0]

    return redondear_dataframe(df_agg)

def calcular_indices(df_diario, lat):
    """
    Calcula índices agroclimáticos incluyendo específicos para Drosophila suzukii.

    Índices calculados:
    - GDD: Grados día (base 10°C), acumulados desde 1 de julio (año agrícola)
    - HF: Horas frío aproximadas, acumuladas desde 1 de mayo
    - VPD: Déficit de presión de vapor (kPa)
    - ETo: Evapotranspiración de referencia Hargreaves (mm)

    Índices D. suzukii:
    - DS_Optimo: Días con T media óptima (18-23°C)
    - DS_Favorable: Días favorables (T 10-30°C y HR > 60%)
    - DS_Estres: Días con estrés térmico (T > 30°C)
    - DS_Inactivo: Días con baja actividad (T < 10°C)
    - DS_Riesgo: Índice de riesgo acumulado
    """
    df = df_diario.copy()
    df['fecha'] = pd.to_datetime(df['fecha'])

    temp_cols = [c for c in df.columns if 'temperatura' in c.lower() and 'aire' in c.lower()]
    tmin_col = next((c for c in temp_cols if 'min' in c.lower()), None)
    tmax_col = next((c for c in temp_cols if 'max' in c.lower()), None)
    tmean_col = next((c for c in temp_cols if 'media' in c.lower()), None)
    hr_col = next((c for c in df.columns if 'humedad' in c.lower() and 'media' in c.lower()), None)

    indices = pd.DataFrame()
    indices['fecha'] = df['fecha']

    # Función para determinar el año agrícola (empieza 1 de julio)
    def anno_agricola(fecha):
        return fecha.year if fecha.month >= 7 else fecha.year - 1

    # Función para determinar el año de horas frío (empieza 1 de mayo)
    def anno_hf(fecha):
        return fecha.year if fecha.month >= 5 else fecha.year - 1

    # ==================== GDD ====================
    if tmin_col and tmax_col:
        indices['GDD'] = df.apply(lambda r: calcular_gdd(r[tmax_col], r[tmin_col], TEMP_BASE_GDD), axis=1)
        # Acumular desde 1 de julio
        indices['Anno_Agr'] = df['fecha'].apply(anno_agricola)
        indices['GDD_Acum'] = indices.groupby('Anno_Agr')['GDD'].cumsum().round(DECIMALES['default'])
        indices = indices.drop(columns=['Anno_Agr'])

    # ==================== HORAS FRÍO ====================
    if tmin_col:
        # Aproximación: T < 7°C = 24h, T < 10°C = 12h, resto = 0h
        indices['HF'] = df[tmin_col].apply(lambda t: 24 if t < TEMP_FRIO else (12 if t < TEMP_FRIO + 3 else 0))
        # Acumular desde 1 de mayo
        indices['Anno_HF'] = df['fecha'].apply(anno_hf)
        indices['HF_Acum'] = indices.groupby('Anno_HF')['HF'].cumsum()
        indices = indices.drop(columns=['Anno_HF'])

    # ==================== VPD ====================
    if tmean_col and hr_col:
        indices['VPD'] = df.apply(lambda r: calcular_vpd(r[tmean_col], r[hr_col]), axis=1)

    # ==================== ETo ====================
    if tmin_col and tmax_col and tmean_col:
        df['doy'] = df['fecha'].dt.dayofyear
        indices['ETo'] = df.apply(lambda r: calcular_eto_hargreaves(r[tmin_col], r[tmax_col], r[tmean_col], lat, r['doy']), axis=1)

    # ==================== ÍNDICES DROSOPHILA SUZUKII ====================
    if tmean_col:
        t_media = df[tmean_col]

        # Días con temperatura óptima para D. suzukii (18-23°C)
        indices['DS_Optimo'] = ((t_media >= 18) & (t_media <= 23)).astype(int)

        # Días con estrés térmico (T > 30°C reduce supervivencia)
        if tmax_col:
            indices['DS_Estres'] = (df[tmax_col] > 30).astype(int)

        # Días con baja actividad (T < 10°C)
        if tmin_col:
            indices['DS_Inactivo'] = (df[tmin_col] < 10).astype(int)

        # Días favorables: T entre 10-30°C Y HR > 60%
        if hr_col and tmin_col and tmax_col:
            hr = df[hr_col]
            t_ok = (df[tmin_col] >= 10) & (df[tmax_col] <= 30)
            hr_ok = hr > 60
            indices['DS_Favorable'] = (t_ok & hr_ok).astype(int)

            # Índice de riesgo: ponderación de condiciones favorables
            # 0-3 puntos por día según condiciones
            riesgo_diario = indices['DS_Optimo'] * 2 + indices['DS_Favorable']
            indices['DS_Riesgo'] = riesgo_diario

            # Acumular riesgo por año agrícola
            indices['Anno_Agr'] = df['fecha'].apply(anno_agricola)
            indices['DS_Riesgo_Acum'] = indices.groupby('Anno_Agr')['DS_Riesgo'].cumsum()
            indices = indices.drop(columns=['Anno_Agr'])

    return indices

# ============================================================================
# GEOPACKAGE
# ============================================================================

def crear_geopackage(stations_df, filepath):
    """Crea un GeoPackage con las estaciones utilizadas."""
    try:
        import geopandas as gpd
        from shapely.geometry import Point

        # Crear geometría de puntos
        geometry = [Point(float(row['longitud']), float(row['latitud']))
                    for _, row in stations_df.iterrows()]

        gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs="EPSG:4326")
        gdf.to_file(filepath, driver="GPKG")
        return True
    except ImportError:
        print("  ⚠️ geopandas no instalado, creando CSV alternativo...")
        # Alternativa: guardar como CSV
        csv_path = filepath.replace('.gpkg', '_estaciones.csv')
        stations_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        return False
    except Exception as e:
        print(f"  ⚠️ Error creando GeoPackage: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("DESCARGA COMPLETA - ÑUBLE Y MAULE - PROYECTO FIA")
    print("="*70)

    # Inicializar cliente con caché
    init_client()

    # Crear directorios
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)
    os.makedirs(GEOPACKAGE_DIR, exist_ok=True)

    stations = get_stations()
    if stations.empty:
        print("Error obteniendo estaciones")
        sys.exit(1)

    # Normalizar regiones (acepta "16", "R16", "Ñuble", etc.)
    regiones_normalizadas = normalize_regions(REGIONES)
    print(f"Regiones: {regiones_normalizadas}")
    stations_filtered = stations[stations['region'].isin(regiones_normalizadas)].reset_index(drop=True)

    if MAX_ESTACIONES > 0:
        stations_filtered = stations_filtered.head(MAX_ESTACIONES).copy()
        print(f"Modo prueba: procesando solo {len(stations_filtered)} estación(es)")

    ubicaciones = cargar_ubicaciones_estaciones()
    total_estaciones = len(stations_filtered)
    print(f"\nEstaciones: {total_estaciones}")

    # Lista para guardar estaciones procesadas (para GeoPackage)
    estaciones_procesadas = []

    for idx, station in stations_filtered.iterrows():
        code = station['identificador']
        name = station['nombre']
        region = station['region']
        lat, lon, elev, primer = resolver_metadatos_estacion(station, ubicaciones)

        print(f"\n{'='*60}")
        print(f"[{idx+1}/{total_estaciones}] {name} ({code}) - {region}")

        variables = get_variables(code)
        if variables.empty:
            print("  Sin variables")
            continue

        try:
            start_year = pd.to_datetime(primer).year
        except:
            start_year = 2015
        end_year = datetime.now().year

        station_data = None

        for _, var in variables.iterrows():
            var_id = var.get('identificador')
            var_name = var.get('nombre', f'var_{var_id}')
            col_name = var_name.replace(" ", "_")[:35]

            print(f"  📥 {var_name}...", end=" ", flush=True)

            all_data = []
            for year in range(start_year, end_year + 1):
                start = f"{year}-01-01"
                end = f"{year}-12-31" if year < end_year else datetime.now().strftime("%Y-%m-%d")
                df = get_data(code, var_id, start, end)
                if not df.empty:
                    all_data.append(df)
                time.sleep(0.2)

            if all_data:
                df = pd.concat(all_data).drop_duplicates(subset=['tiempo'])
                df = df.rename(columns={'valor': col_name})

                # Dirección cardinal
                if 'direcci' in col_name.lower():
                    df[f'{col_name}_cardinal'] = df[col_name].apply(grados_a_cardinal)

                if station_data is None:
                    station_data = df
                else:
                    cols = ['tiempo'] + [c for c in df.columns if c not in station_data.columns]
                    station_data = pd.merge(station_data, df[cols], on='tiempo', how='outer')

                print(f"✓ {len(df):,}")
            else:
                print("sin datos")

        if station_data is not None and len(station_data) > 0:
            station_data = station_data.sort_values('tiempo')

            # Redondear valores
            station_data = redondear_dataframe(station_data)

            safe_name = f"{code}_{name}".replace(" ", "_")
            safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '-'))

            # Marcar día/noche en base a radiación para permitir filtrado posterior
            rad_cols = [c for c in station_data.columns if 'radiaci' in c.lower()]
            if rad_cols:
                rad_col = rad_cols[0]
                station_data['Periodo_Dia_Noche_bin'] = (station_data[rad_col].fillna(0) > 0).astype(int)
                station_data['Periodo_Dia_Noche'] = np.where(
                    station_data['Periodo_Dia_Noche_bin'] == 1,
                    'Dia',
                    'Noche'
                )
            else:
                station_data['Periodo_Dia_Noche_bin'] = np.nan
                station_data['Periodo_Dia_Noche'] = np.nan

            # RAW - ordenar columnas y guardar en CSV y Excel
            df_raw_ordenado = ordenar_columnas(station_data)
            csv_path = os.path.join(DIRS['raw_csv'], f"{safe_name}_raw.csv")
            excel_path = os.path.join(DIRS['raw_excel'], f"{safe_name}_raw.xlsx")
            df_raw_ordenado.to_csv(csv_path, index=False, encoding='utf-8-sig')
            try:
                df_raw_ordenado.to_excel(excel_path, index=False, engine='openpyxl')
            except Exception as e:
                print(f"    (Excel: {e})")
            print(f"\n  RAW: {len(station_data):,} filas (incluye Dia/Noche) (CSV + Excel)")

            # HORARIO + NUBOSIDAD
            df_h = agregar_horario(station_data)
            if not df_h.empty:
                # Calcular nubosidad desde radiación horaria
                if 'Radiación_Media' in df_h.columns:
                    try:
                        df_h = calcular_nubosidad_horaria(df_h, lat, lon, elev)
                    except Exception as e:
                        print(f"  (Nubosidad: {e})")

                df_h_ordenado = ordenar_columnas(df_h)
                csv_path = os.path.join(DIRS['horario_csv'], f"{safe_name}_horario.csv")
                excel_path = os.path.join(DIRS['horario_excel'], f"{safe_name}_horario.xlsx")
                df_h_ordenado.to_csv(csv_path, index=False, encoding='utf-8-sig')
                try:
                    df_h_ordenado.to_excel(excel_path, index=False, engine='openpyxl')
                except Exception:
                    pass
                nub_info = " +Nub" if 'Nubosidad_pct' in df_h.columns else ""
                print(f"  HORARIO: {len(df_h):,} filas{nub_info} (CSV + Excel)")

            # DIARIO
            df_d = agregar_diario(station_data)
            if not df_d.empty:
                # Agregar nubosidad diaria (media) desde datos horarios
                if not df_h.empty and 'Nubosidad_pct' in df_h.columns:
                    df_h_temp = df_h.copy()
                    df_h_temp['tiempo'] = pd.to_datetime(df_h_temp['tiempo'])
                    nub_daily = df_h_temp.set_index('tiempo')['Nubosidad_pct'].resample('D').mean().round(1)
                    nub_daily = nub_daily.reset_index()
                    nub_daily.columns = ['fecha', 'Nubosidad_pct_media']
                    df_d['fecha'] = pd.to_datetime(df_d['fecha'])
                    df_d = pd.merge(df_d, nub_daily, on='fecha', how='left')

                df_d_ordenado = ordenar_columnas(df_d, es_diario=True)
                csv_path = os.path.join(DIRS['diario_csv'], f"{safe_name}_diario.csv")
                excel_path = os.path.join(DIRS['diario_excel'], f"{safe_name}_diario.xlsx")
                df_d_ordenado.to_csv(csv_path, index=False, encoding='utf-8-sig')
                try:
                    df_d_ordenado.to_excel(excel_path, index=False, engine='openpyxl')
                except Exception:
                    pass
                print(f"  DIARIO: {len(df_d):,} filas (CSV + Excel)")

                # INDICES
                df_i = calcular_indices(df_d, lat)
                if not df_i.empty:
                    df_i_ordenado = ordenar_columnas(df_i, es_diario=True)
                    csv_path = os.path.join(DIRS['indices_csv'], f"{safe_name}_indices.csv")
                    excel_path = os.path.join(DIRS['indices_excel'], f"{safe_name}_indices.xlsx")
                    df_i_ordenado.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    try:
                        df_i_ordenado.to_excel(excel_path, index=False, engine='openpyxl')
                    except Exception:
                        pass
                    print(f"  INDICES: {len(df_i):,} filas (CSV + Excel)")

            # Agregar a lista de estaciones procesadas
            estaciones_procesadas.append({
                'codigo': code,
                'nombre': name,
                'region': region,
                'latitud': lat,
                'longitud': lon,
                'elevacion': elev,
                'primer_dato': primer,
                'n_registros': len(station_data)
            })

    # Crear GeoPackage y Excel de estaciones
    if estaciones_procesadas:
        print(f"\n{'='*60}")
        print("Creando archivos de estaciones...")
        df_estaciones = pd.DataFrame(estaciones_procesadas)
        
        # Excel con información de estaciones
        excel_estaciones_path = os.path.join(GEOPACKAGE_DIR, 'estaciones_metadata.xlsx')
        try:
            df_estaciones.to_excel(excel_estaciones_path, index=False, engine='openpyxl')
            print(f"  📊 Excel estaciones: {excel_estaciones_path}")
        except Exception as e:
            print(f"  ⚠️ Error creando Excel: {e}")
        
        # GeoPackage
        gpkg_path = os.path.join(GEOPACKAGE_DIR, 'estaciones_nuble_maule.gpkg')
        if crear_geopackage(df_estaciones, gpkg_path):
            print(f"  🗺️ GeoPackage: {gpkg_path}")
        else:
            csv_path = os.path.join(GEOPACKAGE_DIR, 'estaciones_nuble_maule.csv')
            df_estaciones.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  📄 CSV estaciones: {csv_path}")

    print(f"\n{'='*70}")
    print("COMPLETADO")
    print(f"Carpeta: {os.path.abspath(PROJECT_DIR)}")
    print("  datos/raw/csv/       - 15 minutos (CSV)")
    print("  datos/raw/excel/     - 15 minutos (Excel)")
    print("  datos/horario/csv/   - Agregado horario (CSV)")
    print("  datos/horario/excel/ - Agregado horario (Excel)")
    print("  datos/diario/csv/    - Agregado diario (CSV)")
    print("  datos/diario/excel/  - Agregado diario (Excel)")
    print("  datos/indices/csv/   - Indices (CSV)")
    print("  datos/indices/excel/ - Indices (Excel)")
    print("  geopackage/          - GeoPackage + Excel de estaciones")

if __name__ == "__main__":
    main()
