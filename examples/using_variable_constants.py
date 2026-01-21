"""
Example demonstrating best practices using variable constants.

This example shows how to use the improved API with:
- Named constants instead of magic numbers
- Built-in aggregation support
- Clear documentation
"""

from datetime import datetime, timedelta
from iniamet import (
    INIAClient,
    # Variable ID constants - use these instead of magic numbers!
    VAR_TEMPERATURA_MEDIA,
    VAR_PRECIPITACION,
    VAR_HUMEDAD_RELATIVA,
    VAR_VIENTO_VELOCIDAD_MEDIA,
    VAR_RADIACION_MEDIA,
    # Helper functions
    list_all_variables,
    get_variable_info,
    get_variable_id_by_name
)


def main():
    """Demonstrate best practices for using INIAMET library."""
    
    # Initialize client
    client = INIAClient()
    
    print("=" * 70)
    print("INIAMET Library - Best Practices Example")
    print("=" * 70)
    
    # =========================================================================
    # 1. List all available variables
    # =========================================================================
    print("\n📋 All Available Variables:")
    print("-" * 70)
    all_vars = list_all_variables()
    print(all_vars.to_string(index=False))
    
    # =========================================================================
    # 2. Get detailed information about a variable
    # =========================================================================
    print("\n\n🔍 Variable Information:")
    print("-" * 70)
    temp_info = get_variable_info(VAR_TEMPERATURA_MEDIA)
    print(f"Variable ID: {VAR_TEMPERATURA_MEDIA}")
    print(f"Name: {temp_info['nombre']}")
    print(f"Unit: {temp_info['unidad']}")
    print(f"Description: {temp_info['descripcion']}")
    
    # =========================================================================
    # 3. Find variable by name (fuzzy search)
    # =========================================================================
    print("\n\n🔎 Search Variable by Name:")
    print("-" * 70)
    var_id = get_variable_id_by_name("precipitacion")
    print(f"Searching for 'precipitacion'... Found ID: {var_id}")
    
    var_id = get_variable_id_by_name("viento")
    print(f"Searching for 'viento'... Found ID: {var_id}")
    
    # =========================================================================
    # 4. Download RAW data (15-minute intervals)
    # =========================================================================
    print("\n\n📥 Downloading RAW Temperature Data:")
    print("-" * 70)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    # Using constant instead of magic number!
    raw_temp = client.get_data(
        station="INIA-47",
        variable=VAR_TEMPERATURA_MEDIA,  # Clear and self-documenting
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"Downloaded {len(raw_temp)} raw records")
    print("\nFirst 5 records:")
    print(raw_temp.head())
    
    # =========================================================================
    # 5. Download DAILY aggregated data
    # =========================================================================
    print("\n\n📊 Downloading DAILY Temperature Data:")
    print("-" * 70)
    
    # New feature: built-in aggregation!
    daily_temp = client.get_data(
        station="INIA-47",
        variable=VAR_TEMPERATURA_MEDIA,
        start_date=start_date,
        end_date=end_date,
        aggregation='D'  # Daily aggregation
    )
    
    print(f"Downloaded {len(daily_temp)} daily records")
    print("\nDaily data with min/max:")
    print(daily_temp)
    
    # =========================================================================
    # 6. Download precipitation with daily totals
    # =========================================================================
    print("\n\n🌧️ Downloading Daily Precipitation:")
    print("-" * 70)
    
    daily_precip = client.get_data(
        station="INIA-47",
        variable=VAR_PRECIPITACION,
        start_date=start_date,
        end_date=end_date,
        aggregation='D'  # Daily sums for precipitation
    )
    
    print(f"Downloaded {len(daily_precip)} daily records")
    print("\nDaily precipitation totals:")
    print(daily_precip)
    
    # =========================================================================
    # 7. Download multiple variables efficiently
    # =========================================================================
    print("\n\n📦 Downloading Multiple Variables:")
    print("-" * 70)
    
    variables_to_download = [
        VAR_TEMPERATURA_MEDIA,
        VAR_PRECIPITACION,
        VAR_HUMEDAD_RELATIVA,
        VAR_VIENTO_VELOCIDAD_MEDIA
    ]
    
    for var_id in variables_to_download:
        info = get_variable_info(var_id)
        data = client.get_data(
            station="INIA-47",
            variable=var_id,
            start_date=start_date,
            end_date=end_date,
            aggregation='D'
        )
        print(f"✓ {info['nombre']}: {len(data)} records")
    
    # =========================================================================
    # 8. Monthly aggregation example
    # =========================================================================
    print("\n\n📅 Monthly Temperature Aggregation:")
    print("-" * 70)
    
    # Get 6 months of data
    start_date_monthly = end_date - timedelta(days=180)
    
    monthly_temp = client.get_data(
        station="INIA-47",
        variable=VAR_TEMPERATURA_MEDIA,
        start_date=start_date_monthly,
        end_date=end_date,
        aggregation='M'  # Monthly aggregation
    )
    
    print(f"Downloaded {len(monthly_temp)} monthly records")
    print("\nMonthly temperature summary:")
    print(monthly_temp)
    
    print("\n" + "=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)
    print("\nKEY TAKEAWAYS:")
    print("1. Use VAR_* constants instead of magic numbers (2001, 2002, etc.)")
    print("2. Use aggregation parameter for temporal aggregation")
    print("3. Use list_all_variables() to see all available variables")
    print("4. Use get_variable_info() to get detailed information")
    print("5. Use get_variable_id_by_name() for fuzzy search")


if __name__ == "__main__":
    main()
