#!/usr/bin/env python3
"""
Script automatizado para descargar datos de temperatura horaria de múltiples regiones INIAMET.

Uso:
    python descargar_temperatura_horaria_nuble.py [REGIONES] [FECHA_INICIO] [FECHA_FIN]

Ejemplos:
    # Región específica
    python descargar_temperatura_horaria_nuble.py R16 2025-09-01 2025-10-22

    # Múltiples regiones
    python descargar_temperatura_horaria_nuble.py R07,R08,R09 2025-09-01 2025-10-22

    # Usar valores por defecto (últimos 30 días, región Ñuble)
    python descargar_temperatura_horaria_nuble.py

Este script descarga datos de temperatura horaria, aplica control de calidad completo
y guarda únicamente los datos válidos en formato CSV original.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Agregar el directorio src al path para importar la librería
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from iniamet import INIAClient, RegionalDownloader
from iniamet.utils import REGION_MAP
import pandas as pd

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Descargar datos de temperatura horaria de regiones INIAMET',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python descargar_temperatura_horaria_nuble.py R16
  python descargar_temperatura_horaria_nuble.py R07,R08,R09 2025-09-01 2025-10-22
  python descargar_temperatura_horaria_nuble.py R13 2025-10-01 2025-10-23
        """
    )

    parser.add_argument(
        'regiones',
        nargs='?',
        default='R16',
        help='Códigos de regiones separados por coma (ej: R07,R08,R09) o nombre de región'
    )

    parser.add_argument(
        'fecha_inicio',
        nargs='?',
        default=None,
        help='Fecha de inicio (YYYY-MM-DD). Por defecto: 30 días atrás'
    )

    parser.add_argument(
        'fecha_fin',
        nargs='?',
        default=None,
        help='Fecha de fin (YYYY-MM-DD). Por defecto: hoy'
    )

    return parser.parse_args()

def normalize_region_codes(region_input):
    """Convert region input to list of region codes."""
    regions = []

    # Split by comma if multiple regions
    region_parts = region_input.split(',')

    for part in region_parts:
        part = part.strip()

        # Check if it's already a region code (R01, R02, etc.)
        if part.upper() in REGION_MAP:
            regions.append(part.upper())
        else:
            # Try to find region by name
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

def generate_output_filename(regions, start_date, end_date):
    """Generate automatic filename based on regions and dates."""
    # Convert region codes to names for filename
    region_names = [REGION_MAP.get(r, r) for r in regions]

    # Create region string
    if len(region_names) == 1:
        region_str = region_names[0].replace(' ', '_')
    elif len(region_names) <= 3:
        region_str = '_'.join(region_names).replace(' ', '_')
    else:
        region_str = f"{len(regions)}_regiones"

    # Format dates
    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')

    filename = f"temperatura_horaria_{region_str}_{start_str}_a_{end_str}.csv"
    return filename

def descargar_temperatura_horaria_regiones(regions, start_date, end_date, output_file):
    """
    Descarga datos de temperatura horaria de múltiples regiones.

    Args:
        regions (list): Lista de códigos de regiones
        start_date (str): Fecha de inicio (YYYY-MM-DD)
        end_date (str): Fecha de fin (YYYY-MM-DD)
        output_file (str): Nombre del archivo CSV de salida
    """
    region_names = [REGION_MAP.get(r, r) for r in regions]
    print(f"🚀 Descarga de temperatura horaria - Regiones: {', '.join(region_names)}")
    print(f"📅 Período: {start_date} a {end_date}")

    try:
        # Crear cliente INIAMET
        client = INIAClient()

        all_data = []
        total_stations = 0

        # Procesar cada región
        for region_code in regions:
            region_name = REGION_MAP.get(region_code, region_code)
            print(f"\n📍 Procesando región {region_code}: {region_name}")

            try:
                # Crear downloader regional
                downloader = RegionalDownloader(region_code, client)
                stations = downloader.stations

                print(f"   ✅ {len(stations)} estaciones encontradas")

                if len(stations) == 0:
                    print(f"   ⚠️ No hay estaciones en {region_name}")
                    continue

                total_stations += len(stations)

                # Descargar datos de temperatura horaria
                print(f"   🌡️ Descargando datos de temperatura...")
                data = downloader.download_climate_data(
                    start_date=start_date,
                    end_date=end_date,
                    variables=['temperature'],
                    aggregation='raw'
                )

                if not data.empty:
                    print(f"   ✅ {len(data)} registros descargados")

                    # Aplicar control de calidad
                    print(f"   � Aplicando control de calidad...")
                    from iniamet.qc import QualityControl
                    qc = QualityControl()
                    data_with_qc = qc.apply_all_checks(data, 'temperatura')

                    # Filtrar solo datos válidos
                    clean_data = data_with_qc[data_with_qc['qc_passed'] == True].copy()

                    # Mantener solo columnas originales
                    original_columns = ['tiempo', 'estacion_codigo', 'estacion_nombre', 'region',
                                      'latitud', 'longitud', 'elevacion', 'valor']
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

        # Guardar como CSV
        print(f"\n💾 Guardando datos en: {output_file}")
        final_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Archivo CSV creado exitosamente")

        # Información adicional del archivo
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"   📏 Tamaño del archivo: {file_size:.1f} KB")

        return final_data

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return None
        return None

def main():
    """Función principal del script."""

    # Parsear argumentos
    args = parse_arguments()

    # Normalizar códigos de regiones
    regions = normalize_region_codes(args.regiones)

    # Configurar fechas
    if args.fecha_fin is None:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(args.fecha_fin, '%Y-%m-%d').date()

    if args.fecha_inicio is None:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(args.fecha_inicio, '%Y-%m-%d').date()

    # Generar nombre de archivo automáticamente
    output_filename = generate_output_filename(regions, str(start_date), str(end_date))

    # Crear directorio de salida
    output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d") / "temperatura_horaria_regiones"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / output_filename

    print("=" * 80)
    print("🌡️ DESCARGA AUTOMATIZADA DE TEMPERATURA HORARIA")
    print("=" * 80)
    print(f"📍 Regiones: {', '.join([REGION_MAP.get(r, r) for r in regions])}")
    print(f"📅 Período: {start_date} a {end_date}")
    print(f"📁 Archivo: {output_filename}")
    print("=" * 80)

    # Ejecutar descarga
    data = descargar_temperatura_horaria_regiones(
        regions=regions,
        start_date=str(start_date),
        end_date=str(end_date),
        output_file=str(output_file)
    )

    if data is not None:
        print("\n" + "=" * 80)
        print("✅ DESCARGA COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print(f"📁 Archivo generado: {output_file}")
        print("🎯 El CSV incluye:")
        print("   • Datos horarios de temperatura (°C)")
        print("   • Formato original (solo columnas esenciales)")
        print("   • Solo datos que pasaron control de calidad")
        print(f"   • {len(regions)} regiones procesadas")
        print("\n💡 Próximos pasos:")
        print("   • Abrir el CSV en Excel o software de análisis")
        print("   • Crear gráficos de series temporales")
        print("   • Realizar análisis estadísticos")
        print("   • Comparar entre regiones")
    else:
        print("\n❌ Error en la descarga de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()
            print("❌ No se encontraron estaciones en Ñuble")
            return None

        # Mostrar estaciones disponibles
        print("\n🏛️ Estaciones disponibles:")
        for _, station in stations.iterrows():
            print(f"   • {station['codigo']}: {station['nombre']}")

        # Descargar datos de temperatura horaria (raw = sin agregación)
        print("\n🌡️ Descargando datos de temperatura horaria...")
        print("   (Esto puede tomar varios minutos dependiendo del período)")

        data = downloader.download_climate_data(
            start_date=start_date,
            end_date=end_date,
            variables=['temperature'],  # Solo temperatura
            aggregation='raw'  # Datos horarios sin agregación
        )

        if data.empty:
            print("❌ No se obtuvieron datos de temperatura")
            return None

        print(f"✅ Datos descargados: {len(data)} registros")

        # Aplicar control de calidad si hay datos
        print("🔍 Aplicando control de calidad...")
        try:
            # Primero aplicar QC con todas las columnas para ver el proceso
            from iniamet.qc import QualityControl
            qc = QualityControl()
            data_with_qc = qc.apply_all_checks(data, 'temperatura')

            # Mostrar estadísticas del QC
            qc_summary = qc.get_qc_summary(data_with_qc)
            print(f"   📊 Total registros antes QC: {qc_summary['total']}")
            print(f"   ✅ Registros que pasaron QC: {qc_summary['passed']}")
            print(f"   ❌ Registros rechazados: {qc_summary['total'] - qc_summary['passed']}")

            # Filtrar solo los datos que pasaron todas las pruebas de calidad
            clean_data = data_with_qc[data_with_qc['qc_passed'] == True].copy()

            # Mantener solo las columnas originales (eliminar columnas de QC)
            original_columns = ['tiempo', 'estacion_codigo', 'estacion_nombre', 'region',
                              'latitud', 'longitud', 'elevacion', 'valor']
            clean_data = clean_data[original_columns]

            print(f"✅ Datos finales: {len(clean_data)} registros válidos (formato original)")

        except Exception as e:
            print(f"⚠️ Error en control de calidad: {e}")
            print("   Usando datos sin filtrar...")
            clean_data = data

        # Mostrar estadísticas
        print("\n📊 Estadísticas de los datos:")
        print(f"   • Registros totales: {len(clean_data)}")
        print(f"   • Columnas disponibles: {list(clean_data.columns)}")

        # Contar estaciones con datos
        if 'estacion_codigo' in clean_data.columns:
            print(f"   • Estaciones con datos: {clean_data['estacion_codigo'].nunique()}")
        else:
            print("   • Estaciones con datos: No se pudo determinar")

        if 'tiempo' in clean_data.columns:
            print(f"   • Período: {clean_data['tiempo'].min()} a {clean_data['tiempo'].max()}")

        if 'valor' in clean_data.columns:
            temp_stats = clean_data['valor'].describe()
            print("\n🌡️ Estadísticas de temperatura:")
            print(f"   • Media: {temp_stats['mean']:.1f}°C")
            print(f"   • Mínima: {temp_stats['min']:.1f}°C")
            print(f"   • Máxima: {temp_stats['max']:.1f}°C")
            print(f"   • Valores válidos: {temp_stats['count']:.0f}")

        # Guardar como CSV
        print(f"\n💾 Guardando datos en: {output_file}")
        clean_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Archivo CSV creado exitosamente")

        # Información adicional del archivo
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"   📏 Tamaño del archivo: {file_size:.1f} KB")

        # Mostrar primeras filas como ejemplo
        print("\n📋 Primeras filas del archivo:")
        print(clean_data.head().to_string(index=False))

        return clean_data

    except Exception as e:
        print(f"❌ Error durante la descarga: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Función principal del script."""

    # Crear directorio de salida
    output_dir = Path("outputs") / "2025-10-22" / "temperatura_horaria"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configurar fechas (últimos 30 días por defecto)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    # Archivo de salida
    output_file = output_dir / f"temperatura_horaria_nuble_{start_date}_a_{end_date}.csv"

    print("=" * 70)
    print("🌡️ DESCARGA DE TEMPERATURA HORARIA - REGIÓN ÑUBLE")
    print("=" * 70)

    # Ejecutar descarga
    data = descargar_temperatura_horaria_nuble(
        start_date=str(start_date),
        end_date=str(end_date),
        output_file=str(output_file)
    )

    if data is not None:
        print("\n" + "=" * 70)
        print("✅ DESCARGA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"📁 Archivo generado: {output_file}")
        print("🎯 El CSV incluye:")
        print("   • Datos horarios de temperatura (°C)")
        print("   • Formato original (solo columnas esenciales)")
        print("   • Solo datos que pasaron control de calidad")
        print("   • Todas las estaciones de Ñuble")
        print("\n💡 Próximos pasos:")
        print("   • Abrir el CSV en Excel o software de análisis")
        print("   • Crear gráficos de series temporales")
        print("   • Realizar análisis estadísticos")
        print("   • Comparar entre estaciones")
    else:
        print("\n❌ Error en la descarga de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()
    main()