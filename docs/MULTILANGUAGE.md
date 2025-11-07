# Configuración de Read the Docs para Múltiples Idiomas

Esta configuración permite que la documentación de INIAMET esté disponible en inglés y español.

## Estructura de Idiomas

- **Inglés (en)**: Idioma por defecto
  - Archivo principal: `docs/source/index.rst`
  - URL: https://iniamet.readthedocs.io/en/latest/

- **Español (es)**: Traducción completa
  - Archivo principal: `docs/source/index_es.rst`
  - URL: https://iniamet.readthedocs.io/es/latest/

## Configuración en Read the Docs

### Opción 1: Usar Sphinx con gettext (Recomendado)

1. En Read the Docs Admin → Settings → Advanced Settings
2. Configurar:
   - **Default language**: English
   - **Languages**: Agregar "Spanish"

3. La documentación se construirá automáticamente en ambos idiomas

### Opción 2: Proyectos Separados

Si Read the Docs no detecta automáticamente el español, crear manualmente:

1. **Proyecto Principal (Inglés)**
   - Name: `iniamet`
   - Language: English
   - Configuración: usa `.readthedocs.yaml`

2. **Proyecto Español**
   - Name: `iniamet-es`
   - Language: Spanish
   - Configuración: usa `docs/source/index_es.rst`

3. **Vincular proyectos**
   - En Admin → Translations
   - Agregar `iniamet-es` como traducción de `iniamet`

## Archivos de Documentación

### Inglés
- `docs/source/index.rst` - Página principal en inglés
- `README.md` - README en inglés

### Español
- `docs/source/index_es.rst` - Página principal en español
- `docs/README_ES.md` - README completo en español
- `docs/RECETAS.md` - Recetas y ejemplos en español

## Selector de Idioma

Read the Docs agregará automáticamente un selector de idioma en la parte inferior izquierda de la documentación cuando detecte múltiples idiomas configurados.

## Actualizar Traducciones

Para generar archivos de traducción con gettext:

```bash
# Instalar sphinx-intl
pip install sphinx-intl

# Generar archivos .pot
cd docs
make gettext

# Inicializar/actualizar traducciones al español
sphinx-intl update -p build/gettext -l es

# Traducir archivos en docs/source/locale/es/LC_MESSAGES/*.po

# Construir documentación en español
make -e SPHINXOPTS="-D language='es'" html
```

## Verificación Local

```bash
# Construir en inglés
cd docs
make html

# Construir en español
make -e SPHINXOPTS="-D language='es'" html
```

## Enlaces Útiles

- [Documentación de i18n de Sphinx](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- [Guía de Read the Docs para Localization](https://docs.readthedocs.io/en/stable/guides/manage-translations.html)
