# 📚 INIAMET Library - Documentación Completa

> **Biblioteca Python para acceder a datos agrometeorológicos de estaciones INIA Chile**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Tabla de Contenidos

- [Instalación](#instalación)
- [Inicio Rápido](#inicio-rápido)
- [Clases Principales](#clases-principales)
  - [INIAClient](#iniaclient)
  - [StationManager](#stationmanager)
  - [DataDownloader](#datadownloader)
  - [RegionalDownloader](#regionaldownloader)
  - [QualityControl](#qualitycontrol)
- [Funciones de Utilidad](#funciones-de-utilidad)
- [Funciones de Visualización](#funciones-de-visualización)
- [Constantes](#constantes)
- [Ejemplos Avanzados](#ejemplos-avanzados)
- [Solución de Problemas](#solución-de-problemas)

## 🚀 Instalación

```bash
# Instalar desde código fuente
pip install -e .
```

## ⚡ Inicio Rápido

```python
from iniamet import INIAClient

# Crear cliente
client = INIAClient()

# Obtener estaciones de una región
stations = client.get_stations(region="R16")  # Ñuble
print(f"Encontradas {len(stations)} estaciones")

# Descargar datos de temperatura
data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
print(f"Datos descargados: {len(data)} registros")
```

## 🏗️ Clases Principales

### INIAClient

**Clase principal para acceder a datos agrometeorológicos de INIA.**

#### Constructor
```python
INIAClient(api_key=None, cache=True, cache_dir="./iniamet_cache")
```

**Parámetros:**
- `api_key` (str, opcional): Clave API personalizada
- `cache` (bool): Habilitar/deshabilitar caché (default: True)
- `cache_dir` (str): Directorio para archivos de caché

#### Métodos

##### `get_stations(region=None, station_type=None, force_update=False)`
Obtiene lista de estaciones disponibles con filtros opcionales.

**Parámetros:**
- `region` (str, opcional): Código de región (ej: "R16") o nombre
- `station_type` (str, opcional): Tipo de estación (ej: "INIA", "DMC")
- `force_update` (bool): Forzar actualización desde API

**Retorna:** DataFrame con columnas: codigo, nombre, region, comuna, latitud, longitud, elevacion, tipo

**Ejemplo:**
```python
# Todas las estaciones
all_stations = client.get_stations()

# Estaciones de Ñuble
nuble_stations = client.get_stations(region="R16")

# Solo estaciones INIA
inia_stations = client.get_stations(station_type="INIA")
```

##### `get_variables(station, force_update=False)`
Obtiene variables disponibles para una estación específica.

**Parámetros:**
- `station` (str): Código de estación
- `force_update` (bool): Forzar actualización desde API

**Retorna:** DataFrame con información de variables

##### `get_data(station, variable, start_date, end_date, use_cache=True)`
Descarga datos de series temporales.

**Parámetros:**
- `station` (str): Código de estación
- `variable` (int|str): ID de variable (int) o nombre (str)
- `start_date` (str|datetime): Fecha inicio
- `end_date` (str|datetime): Fecha fin
- `use_cache` (bool): Usar datos en caché

**Retorna:** DataFrame con columnas: tiempo, valor

**Ejemplo:**
```python
# Temperatura por ID
temp_data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")

# Precipitación por nombre
precip_data = client.get_data("INIA-47", "Precipitación", "2024-09-01", "2024-09-30")
```

##### `bulk_download(stations, variables, start_date, end_date, delay=0.5)`
Descarga masiva de datos para múltiples estaciones y variables.

**Parámetros:**
- `stations` (List[str]): Lista de códigos de estaciones
- `variables` (List[int|str]): Lista de variables
- `start_date` (str|datetime): Fecha inicio
- `end_date` (str|datetime): Fecha fin
- `delay` (float): Retardo entre requests (segundos)

**Retorna:** Dict con datos por estación

### StationManager

**Gestor de catálogo de estaciones y consultas.**

#### Métodos

##### `get_stations(...)`
Obtiene estaciones con filtrado opcional.

##### `get_variables(station)`
Obtiene variables disponibles para una estación.

##### `check_variable_exists(station, variable)`
Verifica si una variable existe para una estación.

**Retorna:** True si existe, False si no

### DataDownloader

**Manejador de descargas de datos desde API INIA.**

#### Métodos

##### `get_data(...)`
Descarga datos de series temporales con caché y agregación.

### RegionalDownloader

**Descargador especializado para análisis regionales.**

#### Constructor
```python
RegionalDownloader(region_code, client)
```

#### Métodos

##### `download_climate_data(start_date, end_date, variables, aggregation='D')`
Descarga datos climáticos para toda una región.

**Parámetros:**
- `start_date` (str|datetime): Fecha inicio
- `end_date` (str|datetime): Fecha fin
- `variables` (List[str]): Lista de nombres de variables
- `aggregation` (str): Frecuencia de agregación ('D', 'W', 'M')

**Retorna:** DataFrame con datos regionales consolidados

**Ejemplo:**
```python
from iniamet import RegionalDownloader

downloader = RegionalDownloader("R16", client)
data = downloader.download_climate_data(
    start_date="2024-01-01",
    end_date="2024-12-31",
    variables=['temperature', 'precipitation'],
    aggregation='M'
)
```

### QualityControl

**Sistema completo de control de calidad para datos meteorológicos.**

#### Constructor
```python
QualityControl()
```

#### Métodos

##### `apply_all_checks(data, variable)`
Aplica todas las pruebas de control de calidad.

**Parámetros:**
- `data` (DataFrame): Datos a validar
- `variable` (str): Tipo de variable ('temperature', 'precipitation', etc.)

**Retorna:** DataFrame con datos limpios

##### `get_qc_summary(data)`
Obtiene resumen estadístico del control de calidad.

**Retorna:** Dict con estadísticas de calidad

## 🛠️ Funciones de Utilidad

### `apply_quality_control(data, variable_name, return_clean_only=True)`
Aplica control de calidad a datos meteorológicos.

**Parámetros:**
- `data` (DataFrame): Datos a procesar
- `variable_name` (str): Nombre de variable ('temperatura', 'precipitacion', etc.)
- `return_clean_only` (bool): Retornar solo datos válidos

**Retorna:** DataFrame con datos procesados

**Ejemplo:**
```python
from iniamet import apply_quality_control

# Aplicar QC a datos de temperatura
clean_temp = apply_quality_control(temp_data, 'temperatura')

# Aplicar QC a datos mixtos
clean_mixed = apply_quality_control(mixed_data, 'mixed')
```

### `get_qc_report(data)`
Genera reporte de control de calidad.

**Parámetros:**
- `data` (DataFrame): Datos procesados por QC

**Retorna:** String con reporte formateado

### `get_region_name(region_code)`
Obtiene nombre completo de región desde código.

**Parámetros:**
- `region_code` (str): Código de región (ej: "R16")

**Retorna:** String con nombre completo

**Ejemplo:**
```python
from iniamet import get_region_name

name = get_region_name("R16")  # Retorna: "Ñuble"
```

### `get_variable_info(variable_id)`
Obtiene información detallada de una variable.

**Parámetros:**
- `variable_id` (int): ID de variable

**Retorna:** Dict con información de variable

## 📊 Funciones de Visualización

### `plot_station_map(stations_df, output_file='stations_map.html', zoom_start=6, show_inline=True)`
Crea mapa simple mostrando ubicaciones de estaciones.

**Parámetros:**
- `stations_df` (DataFrame): Datos de estaciones (codigo, nombre, latitud, longitud)
- `output_file` (str): Archivo HTML de salida
- `zoom_start` (int): Nivel de zoom inicial
- `show_inline` (bool): Mostrar mapa inline en Jupyter

**Retorna:** Objeto Map de Folium

**Ejemplo:**
```python
from iniamet import plot_station_map

# Crear mapa de estaciones
stations = client.get_stations(region="R16")
mapa = plot_station_map(stations)
```

### `plot_temperature_map(stations_df, title="Mapa de Temperaturas", zoom_start=6)`
Crea mapa de temperaturas con colores por rangos.

**Parámetros:**
- `stations_df` (DataFrame): Datos con temperaturas (debe incluir columna 'temperatura')
- `title` (str): Título del mapa
- `zoom_start` (int): Nivel de zoom inicial

**Retorna:** Objeto Map de Folium

### `quick_temp_map(client, region='Ñuble', date=None, variable=2002, **map_kwargs)`
Función de alto nivel para crear mapas de temperatura con un solo llamado.

**Parámetros:**
- `client` (INIAClient): Cliente INIA inicializado
- `region` (str): Nombre de región
- `date` (str, opcional): Fecha específica (usa última disponible si None)
- `variable` (int): ID de variable (default: 2002 - temperatura)
- `**map_kwargs`: Parámetros adicionales para el mapa

**Retorna:** Objeto Map de Folium

**Ejemplo:**
```python
from iniamet import quick_temp_map

# Mapa rápido de temperaturas
mapa = quick_temp_map(client, region='Ñuble', date='2024-09-15')
```

## 📋 Constantes

### `REGION_MAP`
Diccionario con códigos y nombres de regiones chilenas.

**Ejemplo:**
```python
from iniamet import REGION_MAP

print(REGION_MAP['R16'])  # Imprime: Ñuble
```

### `VARIABLE_INFO`
Diccionario con información detallada de variables meteorológicas.

**Estructura:**
```python
{
    2001: {
        'nombre': 'Humedad Relativa',
        'unidad': '%',
        'descripcion': 'Humedad relativa del aire'
    },
    2002: {
        'nombre': 'Temperatura',
        'unidad': '°C',
        'descripcion': 'Temperatura del aire'
    },
    # ... más variables
}
```

## 🎯 Ejemplos Avanzados

### Análisis Regional Completo
```python
from iniamet import INIAClient, RegionalDownloader, apply_quality_control
import matplotlib.pyplot as plt

# Configurar cliente
client = INIAClient()

# Análisis regional de Ñuble
downloader = RegionalDownloader("R16", client)
data = downloader.download_climate_data(
    start_date="2024-01-01",
    end_date="2024-12-31",
    variables=['temperature', 'precipitation'],
    aggregation='M'
)

# Aplicar control de calidad
clean_data = apply_quality_control(data, 'mixed')

# Análisis estadístico
monthly_stats = clean_data.groupby(['variable', 'fecha']).agg({
    'valor': ['mean', 'std', 'min', 'max']
})

print("Análisis completado!")
```

### Sistema de Alertas Climáticas
```python
from iniamet import INIAClient, apply_quality_control
from datetime import datetime, timedelta

class ClimateAlertSystem:
    def __init__(self, client):
        self.client = client
        self.alert_thresholds = {
            'heat_wave': 30, 'extreme_heat': 35,
            'cold_wave': 5, 'extreme_cold': 0
        }

    def check_alerts(self, region_code, days_back=3):
        # Obtener datos recientes
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        # Descargar y procesar datos
        stations = self.client.get_stations(region=region_code)
        alerts = []

        for _, station in stations.iterrows():
            try:
                data = self.client.get_data(
                    station['codigo'], 2002, start_date, end_date
                )
                clean_data = apply_quality_control(data, 'temperatura')

                if not clean_data.empty:
                    max_temp = clean_data['valor'].max()
                    min_temp = clean_data['valor'].min()

                    # Verificar alertas
                    if max_temp >= self.alert_thresholds['extreme_heat']:
                        alerts.append({
                            'station': station['codigo'],
                            'type': 'extreme_heat',
                            'temperature': max_temp
                        })

            except Exception as e:
                continue

        return alerts

# Uso
alert_system = ClimateAlertSystem(client)
alerts = alert_system.check_alerts("R16")
print(f"Alertas encontradas: {len(alerts)}")
```

### Visualización Completa
```python
from iniamet import INIAClient, plot_station_map, plot_temperature_map
import pandas as pd

# Crear datos de ejemplo para visualización
client = INIAClient()
stations = client.get_stations(region="R16").head(10)

# Agregar datos de temperatura simulados
stations_with_temp = stations.copy()
stations_with_temp['temperatura'] = [25.5, 22.1, 18.7, 26.3, 21.8,
                                    19.2, 24.9, 23.4, 20.1, 27.0]

# Crear mapas
station_map = plot_station_map(stations)
temp_map = plot_temperature_map(stations_with_temp, title="Temperaturas Ñuble")

print("Mapas creados exitosamente!")
```

## 🔧 Solución de Problemas

### Error: `isinstance() arg 2 must be a type, a tuple of types, or a union`

**Causa:** Datos corruptos en la API de INIAMET para estaciones específicas.

**Solución:** Evitar las siguientes estaciones hasta que INIAMET corrija sus datos:
- CEAZA-MARPCH
- DMC-290013
- CEAZA-PC

**Código de verificación:**
```python
# Verificar si una estación tiene problemas
problematic_stations = ['CEAZA-MARPCH', 'DMC-290013', 'CEAZA-PC']

try:
    data = client.get_data(station_code, variable, start_date, end_date)
    print("Estación OK")
except TypeError as e:
    if "isinstance()" in str(e):
        print("Estación problemática - evitar usar")
```

### Error: `No stations found`

**Causa:** Región no válida o sin estaciones activas.

**Solución:** Verificar código de región en `REGION_MAP`.

### Error: `Variable not found`

**Causa:** Variable no disponible para la estación.

**Solución:** Verificar variables disponibles con `get_variables()`.

### Problemas de Rendimiento

**Solución:** Usar caché activado (comportamiento por defecto).

```python
# Forzar actualización desde API
data = client.get_data(station, variable, start, end, use_cache=False)
```

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles.

## 👥 Contribución

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o reportes de bugs, por favor crear un issue en el repositorio.

---

**Desarrollado por el equipo de datos climáticos INIA** 🌱📊</content>
<parameter name="filePath">g:\Unidades compartidas\Rene\DATOS_CLIMATICOS\ESTACIONES INIA\iniamet-library\FUNCTION_REFERENCE.md