# Recetas y Ejemplos de Uso - INIAMET

Esta guía contiene ejemplos prácticos y recetas para casos de uso comunes con la librería INIAMET.

## 📑 Tabla de Contenidos

- [Descarga Básica](#descarga-básica)
- [Descarga Regional Automatizada](#descarga-regional-automatizada)
- [Control de Calidad](#control-de-calidad)
- [Agregación Temporal](#agregación-temporal)
- [Análisis Multi-Regional](#análisis-multi-regional)
- [Exportar Datos](#exportar-datos)
- [Scripts Automatizados](#scripts-automatizados)

---

## Descarga Básica

### Obtener Estaciones de una Región

```python
from iniamet import INIAClient

client = INIAClient()

# Por código de región
stations_nuble = client.get_stations(region="R16")
print(f"Estaciones en Ñuble: {len(stations_nuble)}")

# Por nombre de región
stations_maule = client.get_stations(region="Maule")
print(f"Estaciones en Maule: {len(stations_maule)}")

# Ver detalles de una estación
for station in stations_nuble[:3]:
    print(f"{station['codigo']}: {station['nombre']} ({station['comuna']})")
```

### Descargar Datos de Temperatura

```python
from iniamet import INIAClient
from datetime import datetime, timedelta

client = INIAClient()

# Último mes de datos
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

data = client.get_data(
    station="INIA-47",  # Chillán
    variable="temperature",
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

print(f"Registros descargados: {len(data)}")
print(data.head())
```

---

## Descarga Regional Automatizada

### Script Completo de Descarga Multi-Regional

Este script descarga datos de temperatura de múltiples regiones con control de calidad completo:

```python
#!/usr/bin/env python3
"""
Script automatizado para descargar datos de temperatura horaria de múltiples regiones INIAMET.

CONFIGURACIÓN:
    Modificar las variables DEFAULT_* al inicio del script para cambiar la configuración.

Uso inteligente de argumentos:
    - Sin argumentos: Usa configuración por defecto
    - Una fecha (YYYY-MM-DD): Se interpreta como fecha de inicio, usa regiones por defecto
    - Un código de región: Usa esa región con fechas por defecto
    - Región + fecha: Especifica región y fecha de inicio
    - Región + fecha_inicio + fecha_fin: Especifica todo

Ejemplos:
    python descargar_temperatura_horaria_regiones.py                    # Configuración por defecto
    python descargar_temperatura_horaria_regiones.py 2025-01-01         # Desde enero (regiones por defecto)
    python descargar_temperatura_horaria_regiones.py R16                # Solo región Ñuble
    python descargar_temperatura_horaria_regiones.py R16 2025-01-01     # Ñuble desde enero
    python descargar_temperatura_horaria_regiones.py R16 2025-01-01 2025-01-31  # Ñuble enero completo

Este script descarga datos de temperatura horaria, aplica control de calidad completo
y guarda únicamente los datos válidos en formato CSV original.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import argparse

from iniamet import INIAClient, RegionalDownloader
from iniamet.utils import REGION_MAP
from iniamet.qc import QualityControl
import pandas as pd

# =============================================================================
# CONFIGURACIÓN DEL SCRIPT - MODIFICAR ESTOS VALORES SEGÚN NECESIDAD
# =============================================================================

# Regiones a procesar (códigos separados por coma)
DEFAULT_REGIONS = "R07,R08,R09,R16"

# Período de tiempo para la descarga
DEFAULT_START_DATE = "2025-01-01"  # Fecha de inicio (YYYY-MM-DD)
DEFAULT_END_DATE = "2025-10-26"    # Fecha de fin (YYYY-MM-DD)

# Tipo de datos de temperatura
USE_HOURLY_AVERAGE = True  # True: promedio horario, False: datos cada 15 minutos

# =============================================================================
# FIN DE CONFIGURACIÓN
# =============================================================================

def parse_arguments():
    """Parsear argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Descargar datos de temperatura horaria de regiones INIAMET',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python script.py                           # Usa configuración por defecto
  python script.py 2025-01-01               # Solo fecha inicio
  python script.py R16                      # Solo región
  python script.py R16 2025-01-01           # Región + fecha inicio
  python script.py R16 2025-01-01 2025-01-31  # Todos los parámetros
        """
    )

    parser.add_argument('regiones', nargs='?', default=None,
                       help='Códigos de regiones separados por coma (ej: R07,R08,R09)')
    parser.add_argument('fecha_inicio', nargs='?', default=None,
                       help='Fecha de inicio (YYYY-MM-DD)')
    parser.add_argument('fecha_fin', nargs='?', default=None,
                       help='Fecha de fin (YYYY-MM-DD)')

    return parser.parse_args()

def normalize_region_codes(region_input):
    """Convertir entrada de región a lista de códigos de región."""
    regions = []
    region_parts = region_input.split(',')

    for part in region_parts:
        part = part.strip()
        
        if part.upper() in REGION_MAP:
            regions.append(part.upper())
        else:
            # Buscar por nombre
            for code, name in REGION_MAP.items():
                if name.lower() == part.lower():
                    regions.append(code)
                    break
            else:
                print(f"⚠️ Región '{part}' no encontrada. Regiones disponibles:")
                for code, name in REGION_MAP.items():
                    print(f"   {code}: {name}")
                sys.exit(1)

    return regions

def generate_output_filename(regions, start_date, end_date, use_hourly_average):
    """Generar nombre de archivo automático basado en regiones y fechas."""
    if len(regions) == 1:
        region_str = regions[0]
    else:
        region_str = '_'.join(regions)

    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')

    agg_type = 'horaria' if use_hourly_average else '15min'
    filename = f"temperatura_{agg_type}_{region_str}_{start_str}_a_{end_str}.csv"
    return filename

def descargar_temperatura_horaria_regiones(regions, start_date, end_date, 
                                          output_file, use_hourly_average=True):
    """
    Descarga datos de temperatura horaria de múltiples regiones.

    Args:
        regions (list): Lista de códigos de regiones
        start_date (str): Fecha de inicio (YYYY-MM-DD)
        end_date (str): Fecha de fin (YYYY-MM-DD)
        output_file (str): Nombre del archivo CSV de salida
        use_hourly_average (bool): True para promedio horario, False para datos cada 15 min
    """
    data_type = "promedio horario" if use_hourly_average else "cada 15 minutos"
    print(f"🚀 Descarga de temperatura {data_type} - Regiones: {', '.join(regions)}")
    print(f"📅 Período: {start_date} a {end_date}")

    try:
        client = INIAClient()
        all_data = []
        
        # Determinar tipo de agregación
        aggregation = 'h' if use_hourly_average else 'raw'

        # Procesar cada región
        for region_code in regions:
            region_name = REGION_MAP.get(region_code, region_code)
            print(f"\n📍 Procesando región {region_code}: {region_name}")

            try:
                downloader = RegionalDownloader(region_code, client)
                stations = downloader.stations

                print(f"   ✅ {len(stations)} estaciones encontradas")

                if len(stations) == 0:
                    print(f"   ⚠️ No hay estaciones en {region_name}")
                    continue

                # Descargar datos de temperatura
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

                    # Mantener solo columnas originales
                    original_columns = ['tiempo', 'estacion_codigo', 'estacion_nombre', 
                                      'region', 'latitud', 'longitud', 'elevacion', 'valor']
                    clean_data = clean_data[original_columns]

                    print(f"   ✅ {len(clean_data)} registros válidos después de QC")
                    all_data.append(clean_data)
                else:
                    print(f"   ⚠️ No se obtuvieron datos para {region_name}")

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

        if 'valor' in final_data.columns:
            temp_stats = final_data['valor'].describe()
            print("\n🌡️ Estadísticas de temperatura:")
            print(f"   • Media: {temp_stats['mean']:.1f}°C")
            print(f"   • Mínima: {temp_stats['min']:.1f}°C")
            print(f"   • Máxima: {temp_stats['max']:.1f}°C")

        # Redondear valores de temperatura a 2 decimales
        if 'valor' in final_data.columns:
            final_data['valor'] = final_data['valor'].round(2)

        # Guardar como CSV
        print(f"\n💾 Guardando datos en: {output_file}")
        final_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Archivo CSV creado exitosamente")

        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"   📏 Tamaño del archivo: {file_size:.1f} KB")

        return final_data

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Función principal del script."""
    args = parse_arguments()

    # Usar configuración por defecto si no se pasan argumentos
    if len(sys.argv) == 1:
        regiones = DEFAULT_REGIONS
        fecha_inicio = DEFAULT_START_DATE
        fecha_fin = DEFAULT_END_DATE
    else:
        # Lógica inteligente para detectar el tipo de argumentos
        if args.regiones and args.fecha_inicio is None and args.fecha_fin is None:
            if args.regiones and len(args.regiones.split('-')) == 3:
                # Parece ser una fecha (formato YYYY-MM-DD)
                regiones = DEFAULT_REGIONS
                fecha_inicio = args.regiones
                fecha_fin = DEFAULT_END_DATE
            else:
                # Parece ser una región
                regiones = args.regiones
                fecha_inicio = DEFAULT_START_DATE
                fecha_fin = DEFAULT_END_DATE
        elif args.regiones and args.fecha_inicio and args.fecha_fin is None:
            regiones = args.regiones
            fecha_inicio = args.fecha_inicio
            fecha_fin = DEFAULT_END_DATE
        else:
            regiones = args.regiones if args.regiones else DEFAULT_REGIONS
            fecha_inicio = args.fecha_inicio if args.fecha_inicio else DEFAULT_START_DATE
            fecha_fin = args.fecha_fin if args.fecha_fin else DEFAULT_END_DATE

    # Normalizar códigos de regiones
    regions = normalize_region_codes(regiones)

    # Configurar fechas
    end_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    start_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()

    # Generar nombre de archivo
    output_filename = generate_output_filename(regions, str(start_date), 
                                              str(end_date), USE_HOURLY_AVERAGE)

    # Crear directorio de salida
    output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / output_filename

    print("=" * 80)
    print("🌡️ DESCARGA AUTOMATIZADA DE TEMPERATURA HORARIA")
    print("=" * 80)
    print(f"📍 Regiones: {', '.join(regions)}")
    print(f"📅 Período: {start_date} a {end_date}")
    print(f"📁 Archivo: {output_filename}")
    print("=" * 80)

    # Ejecutar descarga
    data = descargar_temperatura_horaria_regiones(
        regions=regions,
        start_date=str(start_date),
        end_date=str(end_date),
        output_file=str(output_file),
        use_hourly_average=USE_HOURLY_AVERAGE
    )

    if data is not None:
        print("\n" + "=" * 80)
        print("✅ DESCARGA COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print(f"📁 Archivo generado: {output_file}")
        print("🎯 El CSV incluye:")
        data_type_desc = "promedio horario" if USE_HOURLY_AVERAGE else "cada 15 minutos"
        print(f"   • Datos de temperatura ({data_type_desc})")
        print("   • Solo columnas esenciales")
        print("   • Solo datos que pasaron control de calidad")
        print(f"   • {len(regions)} regiones procesadas")
    else:
        print("\n❌ Error en la descarga de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Control de Calidad

### Aplicar Control de Calidad Completo

```python
from iniamet import INIAClient
from iniamet.qc import QualityControl

# Descargar datos
client = INIAClient()
data = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Crear controlador de calidad
qc = QualityControl()

# Aplicar todas las verificaciones
data_qc = qc.apply_all_checks(data, variable_name='temperatura')

# Ver cuántos datos pasaron QC
total = len(data_qc)
passed = data_qc['qc_passed'].sum()
failed = total - passed

print(f"Total de registros: {total}")
print(f"Pasaron QC: {passed} ({passed/total*100:.1f}%)")
print(f"Fallaron QC: {failed} ({failed/total*100:.1f}%)")

# Filtrar solo datos válidos
datos_limpios = data_qc[data_qc['qc_passed'] == True]

# Guardar
datos_limpios.to_csv('temperatura_limpia.csv', index=False)
```

### Control de Calidad Específico

```python
from iniamet.qc import QualityControl

qc = QualityControl()

# Solo detectar valores extremos (método IQR)
data_qc = qc.detect_extreme_values(data, method='iqr', threshold=3.0)
extremos = data_qc[data_qc['qc_extreme'] == True]
print(f"Valores extremos detectados: {len(extremos)}")

# Solo detectar sensor atascado
data_qc = qc.detect_stuck_sensor(data, window=10, tolerance=0.1)
atascados = data_qc[data_qc['qc_stuck'] == True]
print(f"Valores de sensor atascado: {len(atascados)}")

# Detectar cambios bruscos
data_qc = qc.detect_sudden_changes(data, threshold=10.0)
cambios = data_qc[data_qc['qc_sudden_change'] == True]
print(f"Cambios bruscos detectados: {len(cambios)}")
```

---

## Agregación Temporal

### Resumen Diario, Semanal y Mensual

```python
from iniamet import INIAClient
import pandas as pd

client = INIAClient()

# Descargar datos horarios
data = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    end_date="2024-12-31",
    aggregation="h"  # horario
)

# Asegurar que 'tiempo' sea datetime
data['tiempo'] = pd.to_datetime(data['tiempo'])
data.set_index('tiempo', inplace=True)

# Resumen diario
daily = data['valor'].resample('D').agg(['mean', 'min', 'max'])
daily.columns = ['temp_media', 'temp_min', 'temp_max']

# Resumen semanal
weekly = data['valor'].resample('W').mean()

# Resumen mensual
monthly = data['valor'].resample('M').agg(['mean', 'min', 'max'])

# Guardar
daily.to_csv('temperatura_diaria.csv')
monthly.to_csv('temperatura_mensual.csv')

print("Resumen Mensual:")
print(monthly)
```

---

## Análisis Multi-Regional

### Comparar Temperatura Entre Regiones

```python
from iniamet import INIAClient, RegionalDownloader
import pandas as pd
import matplotlib.pyplot as plt

client = INIAClient()

regiones = ['R07', 'R08', 'R09', 'R16']  # Maule, BioBío, Araucanía, Ñuble
start_date = "2024-09-01"
end_date = "2024-09-30"

datos_regionales = {}

for region_code in regiones:
    downloader = RegionalDownloader(region_code, client)
    
    data = downloader.download_climate_data(
        start_date=start_date,
        end_date=end_date,
        variables=['temperature'],
        aggregation='d'  # promedio diario
    )
    
    if not data.empty:
        # Calcular promedio regional
        data['tiempo'] = pd.to_datetime(data['tiempo'])
        promedio_regional = data.groupby('tiempo')['valor'].mean()
        datos_regionales[region_code] = promedio_regional

# Crear DataFrame combinado
df_comparacion = pd.DataFrame(datos_regionales)

# Graficar
plt.figure(figsize=(12, 6))
df_comparacion.plot()
plt.title('Comparación de Temperatura entre Regiones - Septiembre 2024')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.legend(title='Región')
plt.grid(True)
plt.savefig('comparacion_regiones.png', dpi=300, bbox_inches='tight')
print("Gráfico guardado: comparacion_regiones.png")
```

---

## Exportar Datos

### Exportar a Diferentes Formatos

```python
from iniamet import INIAClient

client = INIAClient()
data = client.get_data(
    station="INIA-47",
    variable="temperature",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# CSV
data.to_csv('temperatura.csv', index=False, encoding='utf-8')

# Excel
data.to_excel('temperatura.xlsx', index=False, sheet_name='Temperatura')

# Parquet (formato comprimido eficiente)
data.to_parquet('temperatura.parquet', index=False)

# JSON
data.to_json('temperatura.json', orient='records', date_format='iso')

print("Datos exportados en múltiples formatos")
```

---

## Scripts Automatizados

### Script con Programación de Tareas

```python
#!/usr/bin/env python3
"""
Script para descarga automatizada diaria de datos meteorológicos.
Usar con cron (Linux/Mac) o Programador de tareas (Windows).

Ejemplo cron (ejecutar diariamente a las 6 AM):
0 6 * * * /usr/bin/python3 /ruta/al/script/descarga_diaria.py
"""

from iniamet import INIAClient, RegionalDownloader
from iniamet.qc import QualityControl
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

def descarga_diaria():
    """Descarga datos del día anterior para todas las regiones configuradas."""
    
    # Configuración
    REGIONES = ['R07', 'R08', 'R09', 'R16']
    VARIABLES = ['temperature', 'precipitation', 'humidity']
    
    # Fecha: ayer
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    # Directorio de salida
    output_dir = Path('datos_diarios') / yesterday.strftime('%Y') / yesterday.strftime('%m')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📅 Descarga de datos para: {date_str}")
    
    client = INIAClient()
    
    for region in REGIONES:
        print(f"\n📍 Procesando región {region}...")
        
        try:
            downloader = RegionalDownloader(region, client)
            
            for variable in VARIABLES:
                print(f"   🌡️ Descargando {variable}...")
                
                data = downloader.download_climate_data(
                    start_date=date_str,
                    end_date=date_str,
                    variables=[variable],
                    aggregation='h'
                )
                
                if not data.empty:
                    # Aplicar QC
                    qc = QualityControl()
                    data_clean = qc.apply_all_checks(data, variable)
                    data_clean = data_clean[data_clean['qc_passed'] == True]
                    
                    # Guardar
                    filename = f"{region}_{variable}_{date_str}.csv"
                    filepath = output_dir / filename
                    data_clean.to_csv(filepath, index=False)
                    print(f"   ✅ Guardado: {filename} ({len(data_clean)} registros)")
                
        except Exception as e:
            print(f"   ❌ Error en {region}: {e}")
            continue
    
    print("\n✅ Descarga diaria completada")

if __name__ == "__main__":
    descarga_diaria()
```

---

## 💡 Consejos y Mejores Prácticas

1. **Usa caché**: El caché automático acelera consultas repetidas
2. **Aplica QC siempre**: El control de calidad mejora la confiabilidad de tus análisis
3. **Descarga por períodos**: Para períodos largos, descarga en chunks mensuales
4. **Verifica datos**: Siempre revisa estadísticas básicas antes de análisis
5. **Guarda metadatos**: Incluye información de estación en tus archivos

---

Para más información, consulta la [documentación completa en español](README_ES.md).
