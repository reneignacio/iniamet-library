"""
==============================================================================
CONVERSIÓN DE RADIACIÓN SOLAR A PORCENTAJE DE NUBOSIDAD (0-100%)
==============================================================================

Metodología:
  1. Modelo de cielo despejado: Ineichen-Perez (via pvlib)
  2. Índice de cielo despejado: Kc = GHI_medida / GHI_cielo_despejado
  3. Nubosidad: Kasten-Czeplak invertida:
     Nubosidad(%) = 100 × [(1 - Kc) / 0.75]^(1/3.4)

Referencias:
  - Crawford & Duchon (1999), J. Appl. Meteorol., 38(4), 474-480.
  - Kasten & Czeplak (1980), Solar Energy, 24(2), 177-189.
  - Ineichen & Perez (2002), Solar Energy, 73, 151-157.

Aplicable a estaciones INIA, DMC y Red Agroclimática Nacional de Chile.
==============================================================================
"""

import os
import json
import pandas as pd
import numpy as np
import pvlib
from pvlib.location import Location
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACIÓN DE ESTACIÓN
# =============================================================================
# Indicar el código de la estación (ej. 'INIA-47') o el nombre (ej. 'Chillán').
# El código tiene prioridad sobre el nombre si ambos están definidos.
# Si no se encuentra la estación, se usan los valores por defecto definidos más abajo.

ESTACION_CODIGO = 'INIA-47'    # Código exacto (ej. 'INIA-47', 'DMC-160010')
ESTACION_NOMBRE = None          # Alternativa: buscar por nombre (substring, sin mayúsculas)
ZONA_HORARIA = 'Etc/GMT+4'      # UTC-4 (Chile continental)

# Valores por defecto si no se encuentra la estación en el archivo
LAT_DEFAULT  = -36.62
LON_DEFAULT  = -72.07
ELEV_DEFAULT = 150.0
NOMBRE_DEFAULT = 'Estación desconocida'

# =============================================================================
# PARÁMETROS DEL MODELO
# =============================================================================
# Umbral mínimo de elevación solar (grados). Por debajo de este ángulo,
# la estimación no es confiable.
ELEVACION_SOLAR_MIN = 5.0

# Umbral mínimo de GHI_clear (W/m²) para evitar divisiones inestables
GHI_CLEAR_MIN = 50.0

# Coeficientes Kasten-Czeplak (valores originales; calibrar localmente si es posible)
COEF_A = 0.75   # promedio sobre todos los tipos de nubes
COEF_B = 3.4    # exponente de la relación potencial

# =============================================================================
# RUTA AL ARCHIVO DE ESTACIONES
# =============================================================================
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)          # descarga_datos_proyecto_FIA/
STATIONS_FILE = os.path.join(_PROJECT_DIR, 'cache', 'stations', 'all_stations.json')


# =============================================================================
# FUNCIÓN: CARGAR COORDENADAS DE ESTACIÓN
# =============================================================================

def cargar_estacion(codigo=None, nombre=None, filepath=STATIONS_FILE):
    """
    Busca una estación en all_stations.json y retorna sus metadatos.

    Prioridad: código exacto > nombre (substring, case-insensitive).

    Parámetros:
    -----------
    codigo : str o None
        Código exacto de la estación (ej. 'INIA-47').
    nombre : str o None
        Nombre o parte del nombre (ej. 'Chillan' coincide con 'Chillán').
    filepath : str
        Ruta al archivo all_stations.json.

    Retorna:
    --------
    dict con claves: lat, lon, elev, nombre, codigo
    """
    if not os.path.exists(filepath):
        print(f"⚠️  Archivo de estaciones no encontrado: {filepath}")
        print(f"   Usando valores por defecto: lat={LAT_DEFAULT}, lon={LON_DEFAULT}, elev={ELEV_DEFAULT}")
        return {
            'lat': LAT_DEFAULT, 'lon': LON_DEFAULT, 'elev': ELEV_DEFAULT,
            'nombre': NOMBRE_DEFAULT, 'codigo': ''
        }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            estaciones = json.load(f)
    except Exception as e:
        print(f"⚠️  Error leyendo archivo de estaciones: {e}")
        return {
            'lat': LAT_DEFAULT, 'lon': LON_DEFAULT, 'elev': ELEV_DEFAULT,
            'nombre': NOMBRE_DEFAULT, 'codigo': ''
        }

    encontrada = None

    # Búsqueda por código exacto (prioridad)
    if codigo:
        for est in estaciones:
            if str(est.get('codigo', '')).strip() == str(codigo).strip():
                encontrada = est
                break
        if encontrada is None:
            print(f"⚠️  Código '{codigo}' no encontrado en el archivo de estaciones.")

    # Búsqueda por nombre (substring, case-insensitive)
    if encontrada is None and nombre:
        nombre_lower = nombre.lower()
        # Normalizar tildes comunes para búsqueda más flexible
        normalize = str.maketrans('áéíóúüñÁÉÍÓÚÜÑ', 'aeiouunAEIOUUN')
        nombre_norm = nombre_lower.translate(normalize)
        for est in estaciones:
            est_nombre = str(est.get('nombre', '')).lower().translate(normalize)
            if nombre_norm in est_nombre:
                encontrada = est
                break
        if encontrada is None:
            print(f"⚠️  Nombre '{nombre}' no encontrado en el archivo de estaciones.")

    if encontrada is None:
        print(f"   Usando valores por defecto: lat={LAT_DEFAULT}, lon={LON_DEFAULT}, elev={ELEV_DEFAULT}")
        return {
            'lat': LAT_DEFAULT, 'lon': LON_DEFAULT, 'elev': ELEV_DEFAULT,
            'nombre': NOMBRE_DEFAULT, 'codigo': ''
        }

    try:
        lat  = float(encontrada.get('latitud',  LAT_DEFAULT))
        lon  = float(encontrada.get('longitud', LON_DEFAULT))
        elev = float(encontrada.get('elevacion', ELEV_DEFAULT))
    except (ValueError, TypeError):
        print(f"⚠️  Coordenadas inválidas para '{encontrada.get('nombre')}'. Usando valores por defecto.")
        lat, lon, elev = LAT_DEFAULT, LON_DEFAULT, ELEV_DEFAULT

    return {
        'lat':    lat,
        'lon':    lon,
        'elev':   elev,
        'nombre': encontrada.get('nombre', NOMBRE_DEFAULT),
        'codigo': encontrada.get('codigo', '')
    }


# =============================================================================
# FUNCIÓN PRINCIPAL: CÁLCULO DE NUBOSIDAD
# =============================================================================

def calcular_nubosidad(df, col_fecha='FechaHora_UTC4', col_rad='Rad',
                       lat=None, lon=None, elev=None, nombre=None, tz=None):
    """
    Calcula el porcentaje de nubosidad a partir de datos de radiación solar.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con columnas de fecha/hora y radiación (W/m²).
    col_fecha : str
        Nombre de la columna de fecha/hora.
    col_rad : str
        Nombre de la columna de radiación global (W/m²).
    lat : float, opcional
        Latitud de la estación. Si es None, se carga desde el archivo de estaciones
        usando ESTACION_CODIGO / ESTACION_NOMBRE definidos en la configuración.
    lon : float, opcional
        Longitud de la estación.
    elev : float, opcional
        Elevación en metros sobre nivel del mar.
    nombre : str, opcional
        Nombre de la estación (solo para mostrar en resultados).
    tz : str, opcional
        Zona horaria (ej. 'Etc/GMT+4'). Por defecto usa ZONA_HORARIA global.

    Retorna:
    --------
    pd.DataFrame con columnas adicionales:
        - GHI_clear     : Radiación teórica de cielo despejado (W/m²)
        - elevacion_solar: Elevación solar (grados)
        - Dia_Noche_bin : 1 día, 0 noche
        - Dia_Noche     : Etiqueta Día/Noche
        - Kc            : Índice de cielo despejado (0-1+)
        - Nubosidad_pct : Porcentaje de nubosidad (0-100)
        - Nubosidad_cat : Categoría simplificada con porcentaje
    """
    # Resolver coordenadas si no se pasaron explícitamente
    if lat is None or lon is None or elev is None:
        info = cargar_estacion(codigo=ESTACION_CODIGO, nombre=ESTACION_NOMBRE)
        lat    = lat    if lat    is not None else info['lat']
        lon    = lon    if lon    is not None else info['lon']
        elev   = elev   if elev   is not None else info['elev']
        nombre = nombre if nombre is not None else info['nombre']

    zona = tz if tz is not None else ZONA_HORARIA

    # --- Preparar índice temporal ---
    data = df.copy()
    data[col_fecha] = pd.to_datetime(data[col_fecha])
    data = data.set_index(col_fecha)
    data.index = data.index.tz_localize(zona)

    # --- Crear objeto Location de pvlib ---
    sitio = Location(
        latitude=lat,
        longitude=lon,
        tz=zona,
        altitude=elev,
        name=nombre or ''
    )

    # --- Calcular posición solar ---
    solar_pos = sitio.get_solarposition(data.index)
    data['elevacion_solar'] = solar_pos['apparent_elevation']
    data['zenith'] = solar_pos['apparent_zenith']

    # --- Calcular radiación de cielo despejado (Ineichen-Perez) ---
    # Usa la turbidez de Linke climatológica incluida en pvlib
    clearsky = sitio.get_clearsky(data.index, model='ineichen')
    data['GHI_clear'] = clearsky['ghi']

    # --- Calcular índice de cielo despejado (Kc) ---
    # Solo donde hay suficiente radiación teórica y sol sobre el horizonte
    es_dia = (data['elevacion_solar'] >= ELEVACION_SOLAR_MIN) & \
             (data['GHI_clear'] >= GHI_CLEAR_MIN)

    data['Dia_Noche_bin'] = es_dia.astype(int)
    data['Dia_Noche'] = np.where(es_dia, 'Dia', 'Noche')

    data['Kc'] = np.nan
    data.loc[es_dia, 'Kc'] = data.loc[es_dia, col_rad] / data.loc[es_dia, 'GHI_clear']

    # Limitar Kc entre 0 y 1.2 (>1 es posible por efecto de realce de nubes)
    data['Kc'] = data['Kc'].clip(0, 1.2)

    # --- Calcular nubosidad con Kasten-Czeplak invertida ---
    data['Nubosidad_pct'] = np.nan

    mask_valido = es_dia & data['Kc'].notna()

    # Cuando Kc >= 1.0 → cielo despejado (0% nubes)
    data.loc[mask_valido & (data['Kc'] >= 1.0), 'Nubosidad_pct'] = 0.0

    # Cuando Kc < 1.0 → aplicar Kasten-Czeplak invertida
    mask_nublado = mask_valido & (data['Kc'] < 1.0)
    ratio = (1.0 - data.loc[mask_nublado, 'Kc']) / COEF_A
    # Limitar ratio a máximo 1 (Kc mínimo implica 100% nubes)
    ratio = ratio.clip(0, 1)
    data.loc[mask_nublado, 'Nubosidad_pct'] = 100.0 * np.power(ratio, 1.0 / COEF_B)

    # Limitar a 0-100%
    data['Nubosidad_pct'] = data['Nubosidad_pct'].clip(0, 100)

    # Noche: se deja NaN (no se puede estimar sin radiación solar)

    # --- Categorías simplificadas + porcentaje ---
    data['Nubosidad_cat'] = 'Noche'
    mask_val = data['Nubosidad_pct'].notna()
    mask_despejado = mask_val & (data['Nubosidad_pct'] <= 20)
    mask_parcial   = mask_val & (data['Nubosidad_pct'] >  20) & (data['Nubosidad_pct'] <= 50)
    mask_nublado   = mask_val & (data['Nubosidad_pct'] >  50) & (data['Nubosidad_pct'] <= 80)
    mask_cubierto  = mask_val & (data['Nubosidad_pct'] >  80)

    data.loc[mask_despejado, 'Nubosidad_cat'] = 'Mayormente despejado'
    data.loc[mask_parcial,   'Nubosidad_cat'] = 'Parcialmente nublado'
    data.loc[mask_nublado,   'Nubosidad_cat'] = 'Nublado'
    data.loc[mask_cubierto,  'Nubosidad_cat'] = 'Cubierto'
    data.loc[mask_val, 'Nubosidad_cat'] = (
        data.loc[mask_val, 'Nubosidad_cat'] +
        ' (' + data.loc[mask_val, 'Nubosidad_pct'].round(0).astype(int).astype(str) + '%)'
    )

    # --- Limpiar y retornar ---
    data = data.drop(columns=['zenith'], errors='ignore')
    data.index = data.index.tz_localize(None)  # quitar timezone para exportar

    return data


# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == '__main__':

    # Cargar metadatos de la estación configurada arriba
    info = cargar_estacion(codigo=ESTACION_CODIGO, nombre=ESTACION_NOMBRE)
    lat_est    = info['lat']
    lon_est    = info['lon']
    elev_est   = info['elev']
    nombre_est = info['nombre']
    codigo_est = info['codigo']

    print("=" * 70)
    print(f"Estación  : {nombre_est} ({codigo_est})")
    print(f"Latitud   : {lat_est}")
    print(f"Longitud  : {lon_est}")
    print(f"Elevación : {elev_est} m s.n.m.")
    print(f"Huso hor. : {ZONA_HORARIA}")
    print("=" * 70)

    # --- Datos de ejemplo ---
    datos_raw = """FechaHora_UTC4,VV,VV_Max,Dir,Pres,PP,Rad,T,HR
2022-01-01 00:00:00,0.3,1.2,228.5,987.4,0,0,12.1,73.3
2022-01-01 01:00:00,0.4,1.2,218.6,987.1,0,0,11.4,76.7
2022-01-01 02:00:00,0.1,0.7,213.4,986.6,0,0,10.6,79.6
2022-01-01 03:00:00,0.1,0.6,213.4,986.4,0,0,10.3,81
2022-01-01 04:00:00,0,0.4,213.4,986.6,0,0,9.4,85.2
2022-01-01 05:00:00,0,0.1,213.4,987.2,0,2.1,7.9,90.2
2022-01-01 06:00:00,0,0.4,213.4,987.9,0,25.1,8.9,89.8
2022-01-01 07:00:00,0.4,1.6,223.9,988.2,0,240.1,13.2,80.8
2022-01-01 08:00:00,0.8,2.5,213,988.1,0,536.8,17.1,67.8
2022-01-01 09:00:00,1,2.9,180.1,988.1,0,720.9,19.8,60.2
2022-01-01 10:00:00,1.2,3.9,203.9,988.1,0,876,21.4,53
2022-01-01 11:00:00,1,2.9,205.7,988.1,0,992.1,23.4,44.2
2022-01-01 12:00:00,1,3.4,209.2,986.8,0,1038.4,25,40.6
2022-01-01 13:00:00,1,3.1,157.9,985.8,0,1012.3,26.6,34.7
2022-01-01 14:00:00,1.2,3.3,157.9,985.3,0,968.5,27.8,32.3
2022-01-01 15:00:00,0.9,2.5,120.4,985.6,0,588.5,27.6,31.7
2022-01-01 16:00:00,1.2,3.6,161.1,985,0,608.8,28.8,28.9
2022-01-01 17:00:00,2.2,4.9,274.8,984.7,0,441.4,27.8,32.6
2022-01-01 18:00:00,2.1,4.5,284,985.2,0,240.1,25.2,37.1
2022-01-01 19:00:00,1.5,4,272.7,986.4,0,45.7,21.8,43.8
2022-01-01 20:00:00,0.6,2.2,210.6,987.5,0,0.7,18.3,56.5
2022-01-01 21:00:00,0.6,1.5,190.9,988.5,0,0,16,67.2
2022-01-01 22:00:00,0.2,0.9,225.7,988.7,0,0,14.5,73.5"""

    from io import StringIO
    df = pd.read_csv(StringIO(datos_raw))

    # --- Ejecutar cálculo pasando las coordenadas obtenidas ---
    resultado = calcular_nubosidad(
        df,
        lat=lat_est,
        lon=lon_est,
        elev=elev_est,
        nombre=nombre_est
    )

    # --- Mostrar resultados ---
    cols_mostrar = ['Rad', 'GHI_clear', 'elevacion_solar', 'Dia_Noche', 'Dia_Noche_bin', 'Kc',
                    'Nubosidad_pct', 'Nubosidad_cat']
    print("\n" + "=" * 90)
    print(f"RESULTADOS - ESTACIÓN {nombre_est} ({lat_est}, {lon_est})")
    print("=" * 90)
    print(resultado[cols_mostrar].to_string(
        float_format=lambda x: f'{x:.1f}' if not np.isnan(x) else 'NaN'
    ))

    # --- Resumen diurno ---
    diurno = resultado[resultado['Nubosidad_pct'].notna()]
    print(f"\n--- Resumen período diurno ---")
    print(f"Horas con estimación: {len(diurno)}")
    if len(diurno) > 0:
        print(f"Nubosidad promedio:   {diurno['Nubosidad_pct'].mean():.1f}%")
        print(f"Nubosidad mínima:     {diurno['Nubosidad_pct'].min():.1f}%")
        print(f"Nubosidad máxima:     {diurno['Nubosidad_pct'].max():.1f}%")

    # --- Exportar a CSV (en la carpeta del script) ---
    safe_nombre = (codigo_est or nombre_est).replace(' ', '_').replace('/', '-')
    out_path = os.path.join(_SCRIPT_DIR, f'resultado_nubosidad_{safe_nombre}.csv')
    resultado.to_csv(out_path, encoding='utf-8-sig')
    print(f"\nResultados exportados a: {out_path}")