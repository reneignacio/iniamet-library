# Guía para Publicar en PyPI

Esta guía te ayudará a publicar la librería `iniamet` en PyPI para que otros puedan instalarla con `pip install iniamet`.

## Requisitos Previos

1. **Cuenta en PyPI**:
   - Crear cuenta en https://pypi.org/account/register/
   - Crear cuenta en https://test.pypi.org/account/register/ (para pruebas)

2. **Token de API (recomendado)**:
   - Ve a https://pypi.org/manage/account/token/
   - Crea un nuevo API token
   - Guárdalo en lugar seguro (solo se muestra una vez)

## Pasos para Publicar

### 1. Instalar Herramientas de Build

```bash
pip install --upgrade build twine
```

### 2. Limpiar Builds Anteriores (si existen)

```bash
# PowerShell
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path src\iniamet.egg-info) { Remove-Item -Recurse -Force src\iniamet.egg-info }
```

### 3. Construir el Paquete

```bash
python -m build
```

Esto creará:
- `dist/iniamet-0.1.0.tar.gz` (código fuente)
- `dist/iniamet-0.1.0-py3-none-any.whl` (wheel)

### 4. Verificar el Paquete

```bash
twine check dist/*
```

### 5. Probar en TestPyPI (RECOMENDADO)

**Configurar credenciales** (crear archivo `.pypirc` en tu home):

```ini
[testpypi]
username = __token__
password = pypi-AgE...  # Tu token de TestPyPI
```

**Subir a TestPyPI**:

```bash
twine upload --repository testpypi dist/*
```

**Probar instalación desde TestPyPI**:

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps iniamet
```

### 6. Publicar en PyPI Real

**IMPORTANTE**: Una vez publicado, NO puedes subir la misma versión de nuevo.

**Opción A - Con archivo .pypirc**:

Agregar a `.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-AgE...  # Tu token de PyPI
```

```bash
twine upload dist/*
```

**Opción B - Con credenciales interactivas**:

```bash
twine upload dist/*
# Username: __token__
# Password: pypi-AgE...  (tu token)
```

### 7. Verificar la Publicación

Visita: https://pypi.org/project/iniamet/

### 8. Instalar desde PyPI

```bash
pip install iniamet
```

## Publicar Nuevas Versiones

1. **Actualizar versión** en `pyproject.toml` y `setup.py`:
   ```toml
   version = "0.1.1"  # Incrementar
   ```

2. **Commit y tag**:
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git tag v0.1.1
   git push origin main --tags
   ```

3. **Reconstruir y publicar**:
   ```bash
   # Limpiar
   Remove-Item -Recurse -Force dist, build, src\iniamet.egg-info
   
   # Build
   python -m build
   
   # Upload
   twine upload dist/*
   ```

## Versionamiento Semántico

- **MAJOR** (1.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (0.1.0): Nueva funcionalidad compatible
- **PATCH** (0.0.1): Correcciones de bugs

## Consejos

1. **Siempre prueba en TestPyPI primero**
2. **Verifica el README** se vea bien en PyPI (usa Markdown)
3. **Revisa los classifiers** en `pyproject.toml`
4. **Mantén actualizado el CHANGELOG**
5. **No incluyas API keys** en el código publicado

## Automatización con GitHub Actions

Puedes crear un workflow para publicar automáticamente cuando crees un tag:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Guarda tu token de PyPI en GitHub Secrets como `PYPI_API_TOKEN`.

## Recursos

- PyPI: https://pypi.org/
- Test PyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/
