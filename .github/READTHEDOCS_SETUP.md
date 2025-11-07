# Configuración de Read the Docs para INIAMET

## ✅ Archivos Creados

Tu repositorio ahora tiene todo lo necesario para Read the Docs:

```
iniamet-library/
├── .readthedocs.yaml          # Configuración de RTD
├── docs/
│   ├── requirements.txt       # Dependencias para build
│   └── source/
│       ├── conf.py           # Configuración de Sphinx
│       ├── index.rst         # Página principal
│       ├── installation.rst  # Guía de instalación
│       ├── quickstart.rst    # Tutorial rápido
│       ├── configuration.rst # Configuración de API key
│       ├── examples.rst      # Ejemplos de uso
│       ├── regions.rst       # Códigos de regiones
│       ├── variables.rst     # Variables disponibles
│       ├── changelog.rst     # Historial de cambios
│       ├── contributing.rst  # Guía de contribución
│       ├── license.rst       # Licencia
│       └── api/             # Documentación de API
│           ├── client.rst
│           ├── stations.rst
│           ├── data.rst
│           ├── qc.rst
│           ├── regional.rst
│           └── utils.rst
```

## 🚀 Pasos para Publicar en Read the Docs

### 1. Push a GitHub

```bash
git push origin main
```

### 2. Ir a Read the Docs

Visita: https://readthedocs.org/

### 3. Importar el Proyecto

1. Haz clic en **"Import a Project"**
2. Si es tu primera vez, conecta tu cuenta de GitHub
3. Selecciona el repositorio `reneignacio/iniamet-library`
4. Haz clic en el botón **"+"** al lado del repositorio

### 4. Configurar el Proyecto

**Configuración básica:**

- **Name**: `iniamet`
- **Repository URL**: `https://github.com/reneignacio/iniamet-library`
- **Default branch**: `main`
- **Default version**: `latest`
- **Programming Language**: `Python`

Haz clic en **"Next"**

### 5. Configuración Avanzada (Opcional)

En **Admin** → **Advanced Settings**:

- ✅ **Build pull requests for this project**
- ✅ **Only build pull requests when there is a new commit**
- **Documentation type**: `Sphinx`
- **Python interpreter**: `CPython 3.12`

### 6. Activar el Proyecto

Haz clic en **"Build version"** para construir la documentación por primera vez.

## 📋 Verificación del Build

### Ver el Log de Build

1. Ve a **Builds** en tu proyecto
2. Verás el build en progreso
3. Haz clic para ver los logs detallados

### Build Exitoso

Deberías ver:

```
Installing dependencies
Building documentation
Build finished successfully
```

### URL de tu Documentación

Una vez completado:
```
https://iniamet.readthedocs.io/en/latest/
```

## 🎨 Personalización

### Badge para README

Agrega este badge a tu `README.md`:

```markdown
[![Documentation Status](https://readthedocs.org/projects/iniamet/badge/?version=latest)](https://iniamet.readthedocs.io/en/latest/?badge=latest)
```

### Custom Domain (Opcional)

En **Admin** → **Domains**:
- Puedes agregar un dominio personalizado
- Ejemplo: `docs.iniamet.cl`

### Versiones

Read the Docs automáticamente creará versiones para:
- **latest**: Última versión en `main`
- **stable**: Última release tag
- Tags específicos (ej: `v0.1.0`)

## 🔧 Mantenimiento

### Actualizar Documentación

Simplemente edita los archivos `.rst` en `docs/source/` y haz push:

```bash
git add docs/source/
git commit -m "docs: update documentation"
git push origin main
```

Read the Docs automáticamente rebuildeará la documentación.

### Rebuild Manual

Si necesitas forzar un rebuild:
1. Ve a tu proyecto en Read the Docs
2. Haz clic en **"Builds"**
3. Haz clic en **"Build Version: latest"**

### Ver Logs de Error

Si el build falla:
1. Ve a **Builds**
2. Haz clic en el build fallido
3. Revisa los logs para ver el error
4. Errores comunes:
   - Faltan dependencias en `docs/requirements.txt`
   - Errores de sintaxis en archivos `.rst`
   - Problemas con imports en `conf.py`

## 📚 Estructura de la Documentación

### Página Principal (`index.rst`)
- Descripción del proyecto
- Features principales
- Quick start
- Tabla de contenidos

### Guías de Usuario
- **Installation**: Instalación del paquete
- **Quick Start**: Tutorial paso a paso
- **Configuration**: Configuración de API key
- **Examples**: Ejemplos prácticos

### Referencia de API
- **Client**: `INIAClient` principal
- **Stations**: Manejo de estaciones
- **Data**: Descarga de datos
- **QC**: Control de calidad
- **Regional**: Descarga regional
- **Utils**: Utilidades

### Información Adicional
- **Regions**: Códigos de regiones chilenas
- **Variables**: Variables meteorológicas disponibles
- **Changelog**: Historial de versiones
- **Contributing**: Guía de contribución
- **License**: Licencia MIT

## 🎯 Características Incluidas

✅ **Autodoc**: Documentación automática desde docstrings
✅ **Type Hints**: Soporte para anotaciones de tipo
✅ **Code Examples**: Ejemplos de código con syntax highlighting
✅ **Search**: Búsqueda integrada
✅ **PDF/ePub**: Exportación a múltiples formatos
✅ **Dark Mode**: Tema RTD con modo oscuro
✅ **Mobile Friendly**: Responsive design
✅ **GitHub Links**: Links automáticos al código fuente

## 🔗 Enlaces Útiles

- **Read the Docs Dashboard**: https://readthedocs.org/dashboard/
- **RTD Documentation**: https://docs.readthedocs.io/
- **Sphinx Documentation**: https://www.sphinx-doc.org/
- **reStructuredText Guide**: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

## 💡 Tips

### Agregar Imágenes

Crea carpeta `docs/source/_static/images/` y agrega:

```rst
.. image:: _static/images/screenshot.png
   :alt: Screenshot
   :align: center
```

### Agregar Tablas

```rst
.. list-table:: Title
   :header-rows: 1

   * - Column 1
     - Column 2
   * - Data 1
     - Data 2
```

### Cross-References

```rst
See :doc:`installation` for more details.
See :ref:`genindex` for full index.
```

### Admonitions

```rst
.. note::
   This is a note.

.. warning::
   This is a warning.

.. tip::
   This is a tip.
```

## ✅ Checklist

Antes de publicar:

- [x] `.readthedocs.yaml` en raíz del repo
- [x] `docs/source/conf.py` configurado
- [x] `docs/requirements.txt` con dependencias
- [x] Archivos `.rst` creados
- [x] Commit y push a GitHub
- [ ] Importar proyecto en Read the Docs
- [ ] Verificar build exitoso
- [ ] Agregar badge al README
- [ ] Compartir URL de documentación

## 🆘 Troubleshooting

### Error: "No module named 'iniamet'"

Asegúrate de que `docs/requirements.txt` incluye:
```
-e .
```

### Error: "Configuration file not found"

Verifica que `.readthedocs.yaml` esté en la raíz del repositorio.

### Error: "Sphinx build failed"

Revisa los logs en Read the Docs y verifica:
- Sintaxis de archivos `.rst`
- Imports en `conf.py`
- Dependencias en `docs/requirements.txt`

### Build tarda mucho

Es normal en el primer build. Builds subsecuentes son más rápidos gracias al caché.

---

**¡Listo!** Tu documentación profesional estará disponible en:
https://iniamet.readthedocs.io/

