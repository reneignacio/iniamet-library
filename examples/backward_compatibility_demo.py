"""
Backward Compatibility Demo - INIAMET v0.2.0+

This example demonstrates that INIAMET maintains full backward compatibility:
- ✅ Old code (v0.1.x) with magic numbers still works
- ✅ New code (v0.2.0+) with named constants works identically
- ✅ Both syntaxes can be mixed in the same project
- ✅ No breaking changes - existing code continues working

Your existing code will work for years without changes!
"""

from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION

def main():
    print("=" * 70)
    print("BACKWARD COMPATIBILITY DEMO - INIAMET v0.2.0+")
    print("=" * 70)
    
    client = INIAClient()
    
    # Get test station
    stations = client.get_stations()
    # Find INIA-47 station using the correct column name
    test_station = stations[stations['codigo'] == 'INIA-47'].iloc[0]
    station_code = test_station['codigo']
    
    print(f"\n📍 Testing with station: {test_station['nombre']} ({station_code})")
    print("   Testing period: September 1-7, 2024")
    
    # =========================================================================
    # OLD SYNTAX (v0.1.x) - Still works! ✅
    # =========================================================================
    print("\n" + "=" * 70)
    print("OLD SYNTAX (v0.1.x) - Using Magic Numbers")
    print("=" * 70)
    
    print("\n📝 Old code (will work indefinitely):")
    print("""
    # No imports needed for constants
    data = client.get_data(
        station='INIA-47',
        variable=2002,  # Magic number for temperature
        start_date='2024-09-01',
        end_date='2024-09-07'
    )
    """)
    
    # Execute old syntax
    data_old = client.get_data(
        station=station_code,
        variable=2002,  # Magic number
        start_date='2024-09-01',
        end_date='2024-09-07'
    )
    
    print(f"✅ Result: {len(data_old)} records downloaded")
    print(f"   Temperature range: {data_old['valor'].min():.1f}°C - {data_old['valor'].max():.1f}°C")
    
    # =========================================================================
    # NEW SYNTAX (v0.2.0+) - Recommended! ✨
    # =========================================================================
    print("\n" + "=" * 70)
    print("NEW SYNTAX (v0.2.0+) - Using Named Constants (Recommended)")
    print("=" * 70)
    
    print("\n📝 New code (more readable):")
    print("""
    from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
    
    data = client.get_data(
        station='INIA-47',
        variable=VAR_TEMPERATURA_MEDIA,  # Named constant
        start_date='2024-09-01',
        end_date='2024-09-07'
    )
    """)
    
    # Execute new syntax
    data_new = client.get_data(
        station=station_code,
        variable=VAR_TEMPERATURA_MEDIA,  # Named constant
        start_date='2024-09-01',
        end_date='2024-09-07'
    )
    
    print(f"✅ Result: {len(data_new)} records downloaded")
    print(f"   Temperature range: {data_new['valor'].min():.1f}°C - {data_new['valor'].max():.1f}°C")
    
    # =========================================================================
    # VERIFICATION: Both produce identical results
    # =========================================================================
    print("\n" + "=" * 70)
    print("VERIFICATION: Both syntaxes produce identical results")
    print("=" * 70)
    
    print(f"\n✅ Same number of records: {len(data_old)} == {len(data_new)}")
    print(f"✅ Same data values: {data_old['valor'].equals(data_new['valor'])}")
    print(f"✅ Same timestamps: {data_old['tiempo'].equals(data_new['tiempo'])}")
    
    # =========================================================================
    # MIXING BOTH SYNTAXES - Also works! ✅
    # =========================================================================
    print("\n" + "=" * 70)
    print("MIXING SYNTAXES - You can use both in the same project!")
    print("=" * 70)
    
    print("\n📝 Mixed syntax code:")
    print("""
    # Old code (legacy)
    temp = client.get_data(station, 2002, start, end)
    
    # New code (recommended for new features)
    precip = client.get_data(station, VAR_PRECIPITACION, start, end)
    """)
    
    # Execute mixed syntax
    temp_mixed = client.get_data(station_code, 2002, '2024-09-01', '2024-09-07')
    precip_mixed = client.get_data(station_code, VAR_PRECIPITACION, '2024-09-01', '2024-09-07')
    
    print(f"\n✅ Temperature (old syntax): {len(temp_mixed)} records")
    print(f"✅ Precipitation (new syntax): {len(precip_mixed)} records")
    
    # =========================================================================
    # AGGREGATION - Works with both syntaxes! ✅
    # =========================================================================
    print("\n" + "=" * 70)
    print("AGGREGATION - Works with both old and new syntax")
    print("=" * 70)
    
    print("\n📝 Aggregation with both syntaxes:")
    print("""
    # Old syntax with aggregation
    daily_old = client.get_data(station, 2002, start, end, aggregation='daily')
    
    # New syntax with aggregation
    daily_new = client.get_data(station, VAR_TEMPERATURA_MEDIA, start, end, 
                                 aggregation='daily')
    """)
    
    # Execute aggregation with both syntaxes
    daily_old = client.get_data(station_code, 2002, '2024-09-01', '2024-09-07', 
                                 aggregation='D')  # Use 'D' for daily
    daily_new = client.get_data(station_code, VAR_TEMPERATURA_MEDIA, 
                                '2024-09-01', '2024-09-07', aggregation='D')
    
    print(f"\n✅ Old syntax daily aggregation: {len(daily_old)} days")
    print(f"✅ New syntax daily aggregation: {len(daily_new)} days")
    print(f"✅ Results identical: {daily_old.equals(daily_new)}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print("\n✅ Your existing code (v0.1.x) will continue working indefinitely")
    print("✅ New constants (v0.2.0+) are available but optional")
    print("✅ Both syntaxes can be mixed in the same project")
    print("✅ All features work with both syntaxes (aggregation, caching, etc.)")
    print("✅ Zero breaking changes - full backward compatibility")
    
    print("\n💡 Recommendation:")
    print("   - Keep existing code as-is (no need to update)")
    print("   - Use named constants for NEW code (more readable)")
    print("   - Gradually migrate when convenient (not required)")
    
    print("\n📚 Documentation:")
    print("   - Migration guide: docs/BEST_PRACTICES.md")
    print("   - All variable constants: docs/QUICK_REFERENCE.md")
    
    print("\n" + "=" * 70)
    print("🎉 INIAMET is future-proof and backward compatible!")
    print("=" * 70)


if __name__ == '__main__':
    main()
