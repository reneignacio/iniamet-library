# Solución de Problemas de Tests en GitHub Actions

## Problemas Identificados

### 1. ❌ Error: `ModuleNotFoundError: No module named 'IPython'`

**Causa**: El módulo `visualization.py` importa `IPython` al inicio, pero esta dependencia no estaba instalada en el entorno de tests de GitHub Actions.

**Solución aplicada**:
- ✅ Convertí `IPython` y `folium` en dependencias **opcionales**
- ✅ Modificado `__init__.py` para importar visualización solo si IPython está disponible
- ✅ Los usuarios pueden instalar con: `pip install iniamet[viz]` si quieren visualización

### 2. ❌ Error: API Key no configurada en tests

**Causa**: Los tests necesitan una API key pero GitHub Actions no tiene una configurada.

**Soluciones aplicadas**:
- ✅ Creado `conftest.py` que automáticamente establece una API key de prueba
- ✅ Agregada variable de entorno `INIA_API_KEY` en el workflow de tests
- ✅ Los tests ahora funcionan sin necesidad de API key real

### 3. ⚠️ URLs incorrectas en PyPI

**Causa**: Las URLs apuntaban a `inia-chile/iniamet` en vez de tu repo real.

**Solución aplicada**:
- ✅ Actualizado `pyproject.toml` con las URLs correctas: `reneignacio/iniamet-library`
- ✅ Actualizado README con links correctos

## Archivos Modificados

### 1. `src/iniamet/__init__.py`
```python
# Antes: Importación directa que fallaba sin IPython
from .visualization import plot_temperature_map, plot_station_map, quick_temp_map

# Ahora: Importación condicional
try:
    from .visualization import plot_temperature_map, plot_station_map, quick_temp_map
    _HAS_VISUALIZATION = True
except ImportError:
    _HAS_VISUALIZATION = False
    plot_temperature_map = None
    plot_station_map = None
    quick_temp_map = None
```

### 2. `pyproject.toml`
```toml
# Antes: folium era dependencia obligatoria
dependencies = [
    "requests>=2.28.0",
    "pandas>=1.5.0",
    "numpy>=1.23.0",
    "folium>=0.14.0",  # ❌ Obligatoria
]

# Ahora: folium e IPython son opcionales
dependencies = [
    "requests>=2.28.0",
    "pandas>=1.5.0",
    "numpy>=1.23.0",
]

[project.optional-dependencies]
viz = [
    "folium>=0.14.0",
    "ipython>=7.0.0",
]
all = [
    "folium>=0.14.0",
    "ipython>=7.0.0",
]
```

### 3. `conftest.py` (NUEVO)
```python
"""Pytest configuration file."""
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_test_api_key():
    """Set a test API key for all tests if not already set."""
    if "INIA_API_KEY" not in os.environ:
        os.environ["INIA_API_KEY"] = "test-api-key-for-ci"
    yield
```

### 4. `.github/workflows/tests.yml`
```yaml
- name: Set test API key
  run: echo "INIA_API_KEY=test-api-key-for-ci-testing" >> $GITHUB_ENV
  shell: bash
```

## Cómo Usar las Nuevas Opciones

### Instalación Básica (sin visualización)
```bash
pip install iniamet
```
**Funciona**: API client, descarga de datos, control de calidad
**No funciona**: Mapas interactivos con folium

### Instalación con Visualización
```bash
pip install iniamet[viz]
```
**Funciona todo**, incluyendo:
- `plot_temperature_map()`
- `plot_station_map()`
- `quick_temp_map()`

### Instalación Completa
```bash
pip install iniamet[all]
```

## Verificación Local

Para verificar que los tests pasan ahora:

```powershell
# 1. Reinstalar el paquete con las dependencias de desarrollo
pip install -e ".[dev]"

# 2. Configurar API key de prueba
$env:INIA_API_KEY='test-api-key-for-ci'

# 3. Ejecutar tests
pytest --cov=iniamet --cov-report=xml --cov-report=html

# Deberías ver:
# ✅ Todos los tests pasan
# ✅ No hay errores de importación
# ✅ Se genera coverage.xml para Codecov
```

## Próximos Pasos

1. **Hacer commit de estos cambios**:
```powershell
git add .
git commit -m "fix: make visualization optional and fix CI tests"
```

2. **Push a GitHub**:
```powershell
git push origin main
```

3. **Verificar GitHub Actions**:
- Ve a: https://github.com/reneignacio/iniamet-library/actions
- Los tests deberían pasar en todas las plataformas (Windows, Linux, macOS)
- Para Python 3.8, 3.9, 3.10, 3.11, 3.12

4. **Publicar en PyPI** (cuando esté listo):
```powershell
# Crear distribución
python -m build

# Publicar
python -m twine upload dist/*
```

## Beneficios de estos Cambios

✅ **Paquete más ligero**: No requiere IPython/folium si solo quieres descargar datos
✅ **Tests robustos**: Funcionan en CI sin API key real
✅ **Mejor experiencia**: Usuarios eligen qué instalar según necesidades
✅ **Compatible**: Funciona en todos los entornos (notebook, script, servidor)

## Resumen de Compatibilidad

| Característica | Instalación Básica | Con [viz] |
|----------------|-------------------|-----------|
| Descargar datos | ✅ | ✅ |
| Control calidad | ✅ | ✅ |
| Pandas DataFrames | ✅ | ✅ |
| Mapas interactivos | ❌ | ✅ |
| Uso en Jupyter | ✅ | ✅ mejor |
| Tests en CI | ✅ | ✅ |

