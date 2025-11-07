# INIAMET - Librería de Datos Agrometeorológicos de INIA Chile

[![Versión Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Versión PyPI](https://badge.fury.io/py/iniamet.svg)](https://pypi.org/project/iniamet/)
[![Estado Documentación](https://readthedocs.org/projects/iniamet/badge/?version=latest)](https://iniamet.readthedocs.io/en/latest/?badge=latest)

**Librería Python de alto nivel para acceder a datos de estaciones agrometeorológicas de INIA (Instituto de Investigaciones Agropecuarias) de Chile.**

> ⚠️ **AVISO IMPORTANTE**: Esta es una **librería NO oficial, desarrollada por la comunidad**. **NO está afiliada, respaldada ni mantenida oficialmente por INIA** (Instituto de Investigaciones Agropecuarias). Esta librería accede a datos públicamente disponibles desde la API agrometeorológica de INIA.

Accede a datos de más de 400 estaciones meteorológicas en todo Chile con una API simple e intuitiva. Descarga temperatura, precipitación, humedad, viento, radiación y más.

## 🌟 Características

- **API de Alto Nivel**: Funciones simples e intuitivas para consultar estaciones y descargar datos
- **Gestión Inteligente de Estaciones**: Maneja automáticamente diferentes formatos de códigos de estación
- **Filtrado Regional**: Filtra estaciones por regiones chilenas (R01-R16)
- **Sistema de Caché**: Sistema de almacenamiento en caché integrado para consultas repetidas más rápidas
- **Tipado Seguro**: Type hints completos para mejor soporte de IDE
- **Integración con pandas**: Retorna datos como DataFrames de pandas
- **Variables Completas**: Temperatura, precipitación, humedad, viento, radiación y más

## 📦 Instalación

```bash
pip install iniamet
```

O instalar desde el código fuente:

```bash
git clone https://github.com/reneignacio/iniamet-library.git
cd iniamet-library
pip install -e .
```

## 🚀 Inicio Rápido

### Ejemplo Básico

```python
from iniamet import INIAClient

# Crear cliente
client = INIAClient()

# Obtener todas las estaciones de la región de Ñuble
stations = client.get_stations(region="R16")
print(f"Estaciones en Ñuble: {len(stations)}")

# Descargar datos de temperatura
data = client.get_data(
    station="INIA-47",  # Estación Chillán
    variable="temperature",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(data.head())
```

### Descarga Regional con Control de Calidad

```python
from iniamet import INIAClient, RegionalDownloader
from iniamet.qc import QualityControl

# Crear cliente y descargador regional
client = INIAClient()
downloader = RegionalDownloader("R16", client)  # Región de Ñuble

# Descargar datos de temperatura (promedio horario)
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=["temperature"],
    aggregation="h"  # 'h' = horario, 'raw' = cada 15 min
)

# Aplicar control de calidad
qc = QualityControl()
data_limpia = qc.apply_all_checks(data, variable_name='temperatura')

# Filtrar solo datos válidos
datos_validos = data_limpia[data_limpia['qc_passed'] == True]

# Guardar a CSV
datos_validos.to_csv('temperatura_nuble_septiembre_2024.csv', index=False)
```

## 📚 Ejemplos Completos

### Script de Descarga Automatizada de Temperatura Regional

Este ejemplo muestra cómo crear un script automatizado para descargar datos de temperatura de múltiples regiones con control de calidad:

```python
#!/usr/bin/env python3
"""
Script automatizado para descargar datos de temperatura horaria de múltiples regiones.

Uso:
    python descargar_temperatura.py                    # Configuración por defecto
    python descargar_temperatura.py 2025-01-01         # Desde fecha específica
    python descargar_temperatura.py R16                # Solo región Ñuble
    python descargar_temperatura.py R16 2025-01-01     # Región y fecha
    python descargar_temperatura.py R16 2025-01-01 2025-01-31  # Período completo
"""

from iniamet import INIAClient, RegionalDownloader
from iniamet.qc import QualityControl
from iniamet.utils import REGION_MAP
import pandas as pd
from datetime import datetime
import sys

# Configuración
DEFAULT_REGIONS = "R07,R08,R09,R16"  # Maule, BioBío, Araucanía, Ñuble
DEFAULT_START_DATE = "2025-01-01"
DEFAULT_END_DATE = "2025-10-26"
USE_HOURLY_AVERAGE = True  # True: promedio horario, False: cada 15 min

def descargar_temperatura_regiones(regions, start_date, end_date, output_file):
    """Descarga datos de temperatura de múltiples regiones con control de calidad."""
    
    print(f"🚀 Descargando temperatura - Regiones: {', '.join(regions)}")
    print(f"📅 Período: {start_date} a {end_date}")
    
    client = INIAClient()
    all_data = []
    
    # Determinar tipo de agregación
    aggregation = 'h' if USE_HOURLY_AVERAGE else 'raw'
    
    # Procesar cada región
    for region_code in regions:
        region_name = REGION_MAP.get(region_code, region_code)
        print(f"\n📍 Procesando {region_code}: {region_name}")
        
        try:
            # Crear descargador regional
            downloader = RegionalDownloader(region_code, client)
            print(f"   ✅ {len(downloader.stations)} estaciones encontradas")
            
            # Descargar datos
            print(f"   🌡️ Descargando datos de temperatura...")
            data = downloader.download_climate_data(
                start_date=start_date,
                end_date=end_date,
                variables=['temperature'],
                aggregation=aggregation
            )
            
            if not data.empty:
                print(f"   ✅ {len(data)} registros descargados")
                
                # Aplicar control de calidad
                print(f"   🔍 Aplicando control de calidad...")
                qc = QualityControl()
                data_with_qc = qc.apply_all_checks(data, 'temperatura')
                
                # Filtrar solo datos válidos
                clean_data = data_with_qc[data_with_qc['qc_passed'] == True].copy()
                
                # Mantener solo columnas esenciales
                columns = ['tiempo', 'estacion_codigo', 'estacion_nombre', 
                          'region', 'latitud', 'longitud', 'elevacion', 'valor']
                clean_data = clean_data[columns]
                
                print(f"   ✅ {len(clean_data)} registros válidos después de QC")
                all_data.append(clean_data)
                
        except Exception as e:
            print(f"   ❌ Error procesando {region_name}: {e}")
            continue
    
    # Combinar todos los datos
    if not all_data:
        print("❌ No se obtuvieron datos de ninguna región")
        return None
    
    final_data = pd.concat(all_data, ignore_index=True)
    
    print(f"\n📊 Datos consolidados:")
    print(f"   • Total de registros: {len(final_data)}")
    print(f"   • Total de estaciones: {final_data['estacion_codigo'].nunique()}")
    print(f"   • Regiones procesadas: {len(regions)}")
    
    # Estadísticas de temperatura
    if 'valor' in final_data.columns:
        stats = final_data['valor'].describe()
        print(f"\n🌡️ Estadísticas de temperatura:")
        print(f"   • Media: {stats['mean']:.1f}°C")
        print(f"   • Mínima: {stats['min']:.1f}°C")
        print(f"   • Máxima: {stats['max']:.1f}°C")
    
    # Guardar a CSV
    print(f"\n💾 Guardando datos en: {output_file}")
    final_data.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ Archivo CSV creado exitosamente")
    
    return final_data

if __name__ == "__main__":
    # Parsear argumentos simples
    regions = DEFAULT_REGIONS.split(',')
    start_date = DEFAULT_START_DATE
    end_date = DEFAULT_END_DATE
    
    if len(sys.argv) > 1:
        if '-' in sys.argv[1] and len(sys.argv[1]) == 10:  # Es una fecha
            start_date = sys.argv[1]
        else:  # Es una región
            regions = sys.argv[1].split(',')
    
    if len(sys.argv) > 2:
        start_date = sys.argv[2]
    
    if len(sys.argv) > 3:
        end_date = sys.argv[3]
    
    # Generar nombre de archivo
    region_str = '_'.join(regions)
    output_file = f"temperatura_{region_str}_{start_date.replace('-', '')}_a_{end_date.replace('-', '')}.csv"
    
    # Ejecutar descarga
    data = descargar_temperatura_regiones(regions, start_date, end_date, output_file)
    
    if data is not None:
        print("\n✅ DESCARGA COMPLETADA EXITOSAMENTE")
        print(f"📁 Archivo: {output_file}")
```

## 🔍 Variables Disponibles

La librería permite acceder a múltiples variables meteorológicas:

### Temperatura
- `'temperature'` - Temperatura del aire (°C)
- `'temperature_max'` - Temperatura máxima
- `'temperature_min'` - Temperatura mínima

### Precipitación
- `'precipitation'` - Precipitación acumulada (mm)

### Humedad
- `'humidity'` - Humedad relativa (%)

### Viento
- `'wind_speed'` - Velocidad del viento (m/s)
- `'wind_direction'` - Dirección del viento (grados)

### Radiación
- `'solar_radiation'` - Radiación solar (W/m²)

### Otras
- `'atmospheric_pressure'` - Presión atmosférica (hPa)
- `'soil_temperature'` - Temperatura del suelo (°C)

## 🗺️ Regiones de Chile

```python
from iniamet.utils import REGION_MAP

# Ver todas las regiones disponibles
for codigo, nombre in REGION_MAP.items():
    print(f"{codigo}: {nombre}")
```

Códigos de regiones:
- `R01`: Tarapacá
- `R02`: Antofagasta
- `R03`: Atacama
- `R04`: Coquimbo
- `R05`: Valparaíso
- `R06`: O'Higgins
- `R07`: Maule
- `R08`: BioBío
- `R09`: Araucanía
- `R10`: Los Lagos
- `R11`: Aysén
- `R12`: Magallanes
- `R13`: Metropolitana
- `R14`: Los Ríos
- `R15`: Arica y Parinacota
- `R16`: Ñuble

## 🛠️ Control de Calidad

La librería incluye un sistema completo de control de calidad:

```python
from iniamet.qc import QualityControl

qc = QualityControl()

# Detectar valores extremos
data_qc = qc.detect_extreme_values(data, method='iqr')

# Detectar sensor atascado
data_qc = qc.detect_stuck_sensor(data)

# Detectar cambios bruscos
data_qc = qc.detect_sudden_changes(data)

# Aplicar todas las verificaciones
data_clean = qc.apply_all_checks(data, variable_name='temperatura')
```

## 📊 Agregación Temporal

```python
# Datos cada 15 minutos (raw)
data_15min = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    aggregation="raw"
)

# Promedio horario
data_hourly = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    aggregation="h"
)

# Promedio diario
data_daily = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    aggregation="d"
)
```

## 💾 Caché de Datos

La librería incluye un sistema de caché automático:

```python
from iniamet import INIAClient

# Con caché (por defecto)
client = INIAClient(use_cache=True)

# Sin caché
client = INIAClient(use_cache=False)

# Personalizar directorio de caché
client = INIAClient(cache_dir="mi_cache_personal")
```

## 🔗 Enlaces

- **Paquete PyPI**: [https://pypi.org/project/iniamet/](https://pypi.org/project/iniamet/)
- **Documentación API**: [INIA Agromet API v2](https://agromet.inia.cl/api/v2)
- **Sitio Oficial INIA**: [https://www.inia.cl](https://www.inia.cl)
- **Repositorio GitHub**: [https://github.com/reneignacio/iniamet-library](https://github.com/reneignacio/iniamet-library)
- **Reporte de Issues**: [GitHub Issues](https://github.com/reneignacio/iniamet-library/issues)

## 📧 Contacto

Para preguntas y soporte, por favor abre un issue en GitHub.

## ⚖️ Aviso Legal

**Esta es una librería NO OFICIAL**. Este proyecto:
- NO está afiliado con INIA (Instituto de Investigaciones Agropecuarias)
- NO está respaldado ni mantenido por INIA
- Es una herramienta independiente desarrollada por la comunidad
- Accede a datos públicamente disponibles desde la API de INIA

Todos los datos accedidos a través de esta librería pertenecen a INIA. Por favor, consulta los términos de servicio de INIA para las políticas de uso de datos.

## 📄 Licencia

MIT License - ver archivo [LICENSE](../LICENSE) para más detalles.

---

Hecho con ❤️ por la comunidad para la comunidad de investigación.
