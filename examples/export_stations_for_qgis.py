"""
Exportar estaciones a CSV para importar en QGIS.

Este script genera un archivo CSV con todas las estaciones incluyendo
coordenadas (lat/lon), nombre, región, institución y otros atributos
listos para visualizar en QGIS.

Autor: INIA
Fecha: 2024
"""

from iniamet import INIAClient
import pandas as pd


def export_stations_for_qgis(regions=None, output_file='estaciones_qgis.csv'):
    """
    Exporta estaciones a CSV listo para QGIS.
    
    Args:
        regions: Lista de regiones a incluir. Si None, exporta todas.
        output_file: Nombre del archivo CSV de salida.
        
    Returns:
        DataFrame con las estaciones exportadas.
    """
    # Initialize client
    client = INIAClient()
    
    # Get all stations
    all_stations = client.get_stations()
    
    # Filter by regions if specified
    if regions is not None:
        all_stations = all_stations[all_stations['region'].isin(regions)].copy()
    
    # Extract institution from codigo (prefix before "-")
    all_stations['institucion'] = all_stations['codigo'].str.split('-').str[0]
    
    # Rename columns for better QGIS compatibility
    qgis_data = all_stations.rename(columns={
        'codigo': 'cod_estacion',
        'nombre': 'nombre_estacion',
        'region': 'region',
        'comuna': 'comuna',
        'latitud': 'lat',
        'longitud': 'lon',
        'elevacion': 'elevacion_m',
        'tipo': 'tipo',
        'primera_lectura': 'fecha_inicio',
        'institucion': 'institucion'
    })
    
    # Select and reorder columns for QGIS
    columns_order = [
        'cod_estacion',
        'nombre_estacion',
        'institucion',
        'region',
        'comuna',
        'lat',
        'lon',
        'elevacion_m',
        'tipo',
        'fecha_inicio'
    ]
    
    qgis_data = qgis_data[columns_order]
    
    # Export to CSV (UTF-8 with BOM for Excel compatibility)
    qgis_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✓ Archivo CSV exportado: {output_file}")
    print(f"✓ Total de estaciones: {len(qgis_data)}")
    
    return qgis_data


def export_regions_for_qgis(regions=None, output_file='estaciones_regiones_qgis.csv'):
    """
    Exporta estaciones de regiones específicas con análisis adicional.
    
    Args:
        regions: Lista de regiones a incluir.
        output_file: Nombre del archivo CSV de salida.
    """
    if regions is None:
        regions = ['Maule', 'Biobío', 'Ñuble', 'La Araucanía']
    
    # Export data
    qgis_data = export_stations_for_qgis(regions=regions, output_file=output_file)
    
    # Print summary by region
    print("\n" + "=" * 80)
    print("RESUMEN POR REGIÓN")
    print("=" * 80)
    for region in regions:
        count = len(qgis_data[qgis_data['region'] == region])
        print(f"  {region}: {count} estaciones")
    
    # Print summary by institution
    print("\n" + "=" * 80)
    print("RESUMEN POR INSTITUCIÓN")
    print("=" * 80)
    inst_counts = qgis_data['institucion'].value_counts()
    for inst, count in inst_counts.items():
        print(f"  {inst}: {count} estaciones")
    
    print("\n" + "=" * 80)
    print("INSTRUCCIONES PARA IMPORTAR EN QGIS")
    print("=" * 80)
    print("""
1. Abrir QGIS
2. Layer → Add Layer → Add Delimited Text Layer
3. Seleccionar el archivo: {output_file}
4. Configurar:
   - File Format: CSV
   - Geometry Definition: Point coordinates
   - X field: lon
   - Y field: lat
   - Geometry CRS: EPSG:4326 - WGS 84
5. Click "Add"
    
El mapa mostrará todas las estaciones con sus atributos.
Puedes usar 'institucion' o 'region' para categorizar los puntos.
""".format(output_file=output_file))


def main():
    """Función principal."""
    print("=" * 80)
    print("EXPORTAR ESTACIONES PARA QGIS")
    print("=" * 80)
    print()
    
    # Option 1: Export all stations
    print("1. Exportando TODAS las estaciones...")
    all_data = export_stations_for_qgis(
        regions=None,
        output_file='estaciones_todas_qgis.csv'
    )
    print(f"   Regiones únicas: {all_data['region'].nunique()}")
    print(f"   Instituciones únicas: {all_data['institucion'].nunique()}")
    
    print("\n" + "-" * 80 + "\n")
    
    # Option 2: Export only 4 south-central regions
    print("2. Exportando estaciones de 4 regiones centrales...")
    export_regions_for_qgis(
        regions=['Maule', 'Biobío', 'Ñuble', 'La Araucanía'],
        output_file='estaciones_regiones_centro_sur_qgis.csv'
    )
    
    print("\n" + "=" * 80)
    print("✓ EXPORTACIÓN COMPLETADA")
    print("=" * 80)
    print("\nArchivos generados:")
    print("  1. estaciones_todas_qgis.csv - Todas las estaciones de Chile")
    print("  2. estaciones_regiones_centro_sur_qgis.csv - Solo Maule, Biobío, Ñuble, La Araucanía")
    print()


if __name__ == "__main__":
    main()
