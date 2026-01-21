"""
Contar estaciones únicas por institución y región.

Este script genera una tabla con el conteo de estaciones únicas
desagregadas por institución y región, usando la fuente interna
de la librería iniamet.

Autor: INIA
Fecha: 2024
"""

from iniamet import INIAClient
import pandas as pd


def generate_station_count_table(regions=None, export_csv=False, output_file=None):
    """
    Genera tabla de conteo de estaciones por institución y región.
    
    Args:
        regions: Lista de regiones a incluir. Si None, usa las 4 regiones por defecto.
        export_csv: Si True, exporta la tabla a CSV.
        output_file: Nombre del archivo CSV de salida.
        
    Returns:
        DataFrame con la tabla pivotada.
    """
    # Initialize client
    client = INIAClient()
    
    # Get all stations from internal API
    all_stations = client.get_stations()
    
    # Define target regions (default: 4 south-central regions)
    if regions is None:
        regions = ['Maule', 'Biobío', 'Ñuble', 'La Araucanía']
    
    # Filter stations for target regions
    filtered_stations = all_stations[all_stations['region'].isin(regions)].copy()
    
    # Extract institution from codigo (prefix before "-")
    filtered_stations['institucion'] = filtered_stations['codigo'].str.split('-').str[0]
    
    # Create pivot table: count unique stations (codigo) by institution and region
    pivot_table = filtered_stations.pivot_table(
        index='institucion',
        columns='region',
        values='codigo',
        aggfunc='nunique',  # Count unique station codes
        fill_value=0
    )
    
    # Ensure columns are in the requested order
    pivot_table = pivot_table.reindex(columns=regions, fill_value=0)
    
    # Add Total column (sum across regions for each institution)
    pivot_table['Total'] = pivot_table.sum(axis=1)
    
    # Add Total row (sum down each region column)
    total_row = pivot_table.sum(axis=0)
    total_row.name = 'Total región'
    pivot_table = pd.concat([pivot_table, pd.DataFrame(total_row).T])
    
    # Rename index to match format
    pivot_table.index.name = 'Institución'
    
    # Convert to integers for cleaner display
    pivot_table = pivot_table.astype(int)
    
    # Export to CSV if requested
    if export_csv:
        if output_file is None:
            output_file = 'estaciones_por_institucion_region.csv'
        pivot_table.to_csv(output_file, encoding='utf-8-sig')
        print(f"\n✓ Tabla exportada a: {output_file}")
    
    return pivot_table, filtered_stations


def print_report(pivot_table, filtered_stations, regions):
    """Imprime reporte formateado."""
    print("=" * 80)
    print("ESTACIONES ÚNICAS POR INSTITUCIÓN Y REGIÓN")
    print("=" * 80)
    print()
    print(pivot_table.to_string())
    print()
    print("=" * 80)
    print(f"\nNotas:")
    print(f"- Total de estaciones únicas: {len(filtered_stations)}")
    print(f"- Instituciones identificadas: {len(pivot_table) - 1}")  # -1 for total row
    print(f"- Regiones analizadas: {', '.join(regions)}")
    print(f"- Fuente: API interna de la librería iniamet")
    print(f"- Criterio de conteo: nunique() sobre campo 'codigo'")
    print(f"- Institución extraída del prefijo antes del '-' en el código")
    print()


def main():
    """Función principal."""
    # Define regions to analyze
    regions = ['Maule', 'Biobío', 'Ñuble', 'La Araucanía']
    
    # Generate table
    pivot_table, filtered_stations = generate_station_count_table(
        regions=regions,
        export_csv=True,
        output_file='estaciones_por_institucion_region.csv'
    )
    
    # Print formatted report
    print_report(pivot_table, filtered_stations, regions)
    
    # Additional analysis: Show top 5 institutions
    print("=" * 80)
    print("TOP 5 INSTITUCIONES POR NÚMERO DE ESTACIONES")
    print("=" * 80)
    
    # Exclude the total row
    top_institutions = pivot_table[pivot_table.index != 'Total región']['Total'].sort_values(ascending=False).head(5)
    for i, (inst, count) in enumerate(top_institutions.items(), 1):
        print(f"{i}. {inst}: {count} estaciones")
    print()
    
    # Show detailed breakdown by region
    print("=" * 80)
    print("DESGLOSE DETALLADO POR REGIÓN")
    print("=" * 80)
    for region in regions:
        total = pivot_table.loc['Total región', region]
        print(f"\n{region}: {total} estaciones")
        
        # Show top 3 institutions in this region
        region_data = pivot_table[pivot_table.index != 'Total región'][region].sort_values(ascending=False).head(3)
        for inst, count in region_data.items():
            if count > 0:
                print(f"  - {inst}: {count}")
    print()


if __name__ == "__main__":
    main()
