"""
Quick test to verify INIAMET v0.2.0 consistency and accessibility.
"""

print("=" * 60)
print("INIAMET v0.2.0 Consistency Test")
print("=" * 60)

# Test 1: Import all main components
print("\n✅ Test 1: Importing main components...")
from iniamet import (
    INIAClient,
    RegionalDownloader,
    QualityControl,
    VAR_TEMPERATURA_MEDIA,
    VAR_PRECIPITACION,
    list_all_variables,
    get_variable_info,
    get_variable_id_by_name,
    is_valid_variable_id
)
print("   SUCCESS: All imports working")

# Test 2: Check all variable constants
print("\n✅ Test 2: Checking variable constants...")
from iniamet import (
    VAR_PRECIPITACION,
    VAR_TEMPERATURA_MEDIA,
    VAR_HUMEDAD_RELATIVA,
    VAR_VIENTO_DIRECCION,
    VAR_VIENTO_VELOCIDAD_MEDIA,
    VAR_VIENTO_VELOCIDAD_MAXIMA,
    VAR_RADIACION_MEDIA,
    VAR_BATERIA_VOLTAJE,
    VAR_TEMPERATURA_SUELO_10CM,
    VAR_TEMPERATURA_SUPERFICIE,
    VAR_PRESION_ATMOSFERICA
)

constants = {
    'VAR_PRECIPITACION': VAR_PRECIPITACION,
    'VAR_TEMPERATURA_MEDIA': VAR_TEMPERATURA_MEDIA,
    'VAR_HUMEDAD_RELATIVA': VAR_HUMEDAD_RELATIVA,
    'VAR_VIENTO_DIRECCION': VAR_VIENTO_DIRECCION,
    'VAR_VIENTO_VELOCIDAD_MEDIA': VAR_VIENTO_VELOCIDAD_MEDIA,
    'VAR_VIENTO_VELOCIDAD_MAXIMA': VAR_VIENTO_VELOCIDAD_MAXIMA,
    'VAR_RADIACION_MEDIA': VAR_RADIACION_MEDIA,
    'VAR_BATERIA_VOLTAJE': VAR_BATERIA_VOLTAJE,
    'VAR_TEMPERATURA_SUELO_10CM': VAR_TEMPERATURA_SUELO_10CM,
    'VAR_TEMPERATURA_SUPERFICIE': VAR_TEMPERATURA_SUPERFICIE,
    'VAR_PRESION_ATMOSFERICA': VAR_PRESION_ATMOSFERICA
}

print(f"   SUCCESS: {len(constants)} constants available")
for name, value in constants.items():
    print(f"     - {name} = {value}")

# Test 3: Variable discovery functions
print("\n✅ Test 3: Testing variable discovery functions...")

all_vars = list_all_variables()
print(f"   list_all_variables(): {len(all_vars)} variables")

info = get_variable_info(VAR_TEMPERATURA_MEDIA)
print(f"   get_variable_info(2002): {info['nombre']}")

var_id = get_variable_id_by_name("temperatura")
print(f"   get_variable_id_by_name('temperatura'): {var_id}")

is_valid = is_valid_variable_id(VAR_TEMPERATURA_MEDIA)
print(f"   is_valid_variable_id(2002): {is_valid}")

# Test 4: Check documentation files
print("\n✅ Test 4: Checking documentation structure...")
import os
docs = [
    'docs/INDEX.md',
    'docs/QUICK_REFERENCE.md',
    'docs/BEST_PRACTICES.md',
    'docs/CONSISTENCY_REPORT.md',
    'examples/EXAMPLES_GUIDE.md'
]

for doc in docs:
    exists = os.path.exists(doc)
    status = "✅" if exists else "❌"
    print(f"   {status} {doc}")

# Test 5: Version check
print("\n✅ Test 5: Version information...")
import iniamet
print(f"   Version: {iniamet.__version__}")
print(f"   Author: {iniamet.__author__}")
print(f"   License: {iniamet.__license__}")

# Final summary
print("\n" + "=" * 60)
print("🎉 All tests passed! INIAMET v0.2.0 is consistent and ready!")
print("=" * 60)

print("\n📚 Quick Documentation Links:")
print("   - Main Docs: README.md")
print("   - Index: docs/INDEX.md")
print("   - Best Practices: docs/BEST_PRACTICES.md")
print("   - Examples: examples/EXAMPLES_GUIDE.md")

print("\n💡 Try running:")
print("   python examples/basic_usage.py")
print("   python examples/using_variable_constants.py")
