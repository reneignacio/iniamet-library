"""
Utility functions for the INIAMET library.
"""

from datetime import datetime, date
from typing import Union, Optional


# Region code mapping
REGION_MAP = {
    "R01": "Tarapacá",
    "R02": "Antofagasta",
    "R03": "Atacama",
    "R04": "Coquimbo",
    "R05": "Valparaíso",
    "R06": "O'Higgins",
    "R07": "Maule",
    "R08": "Biobío",
    "R09": "La Araucanía",
    "R10": "Los Lagos",
    "R11": "Aysén",
    "R12": "Magallanes",
    "R13": "Metropolitana",
    "R14": "Los Ríos",
    "R15": "Arica y Parinacota",
    "R16": "Ñuble"
}

# ============================================================================
# VARIABLE ID CONSTANTS - Use these constants instead of magic numbers
# ============================================================================
# Precipitation
VAR_PRECIPITACION = 2001

# Temperature
VAR_TEMPERATURA_MEDIA = 2002
VAR_TEMPERATURA_SUELO_10CM = 2027
VAR_TEMPERATURA_SUPERFICIE = 2077

# Humidity
VAR_HUMEDAD_RELATIVA = 2007

# Wind
VAR_VIENTO_DIRECCION = 2012
VAR_VIENTO_VELOCIDAD_MEDIA = 2013
VAR_VIENTO_VELOCIDAD_MAXIMA = 2014

# Radiation
VAR_RADIACION_MEDIA = 2022

# Pressure
VAR_PRESION_ATMOSFERICA = 2125

# Other
VAR_BATERIA_VOLTAJE = 2024

# ============================================================================
# VARIABLE METADATA - Complete information about each variable
# ============================================================================
VARIABLE_INFO = {
    2001: {
        'nombre': 'Precipitación',
        'unidad': 'mm',
        'color': 'green',
        'descripcion': 'Precipitación acumulada'
    },
    2002: {
        'nombre': 'Temperatura del Aire Media',
        'unidad': '°C',
        'color': 'red',
        'descripcion': 'Temperatura del aire media'
    },
    2007: {
        'nombre': 'Humedad Relativa Media',
        'unidad': '%',
        'color': 'blue',
        'descripcion': 'Humedad relativa del aire media'
    },
    2012: {
        'nombre': 'Dirección del Viento',
        'unidad': '°',
        'color': 'cyan',
        'descripcion': 'Dirección del viento'
    },
    2013: {
        'nombre': 'Velocidad Viento Media',
        'unidad': 'm/s',
        'color': 'purple',
        'descripcion': 'Velocidad del viento media'
    },
    2014: {
        'nombre': 'Velocidad Viento Máxima',
        'unidad': 'm/s',
        'color': 'purple',
        'descripcion': 'Velocidad del viento máxima'
    },
    2022: {
        'nombre': 'Radiación Media',
        'unidad': 'W/m²',
        'color': 'orange',
        'descripcion': 'Radiación solar media'
    },
    2024: {
        'nombre': 'Batería Voltaje Mínima',
        'unidad': 'V',
        'color': 'gray',
        'descripcion': 'Voltaje mínimo de batería'
    },
    2027: {
        'nombre': 'Temperatura Suelo 10cm Media',
        'unidad': '°C',
        'color': 'brown',
        'descripcion': 'Temperatura del suelo a 10cm media'
    },
    2077: {
        'nombre': 'Temperatura Superficie Media',
        'unidad': '°C',
        'color': 'pink',
        'descripcion': 'Temperatura de superficie media'
    },
    2125: {
        'nombre': 'Presión Atmosférica',
        'unidad': 'mbar',
        'color': 'brown',
        'descripcion': 'Presión atmosférica'
    }
}


def get_variable_info(variable_id: int) -> dict:
    """
    Get metadata for a variable ID.
    
    Args:
        variable_id: Variable ID from INIA API (e.g., 2002, 2001)
        
    Returns:
        Dictionary with variable metadata:
        - nombre: Human-readable name
        - unidad: Measurement unit
        - color: Suggested color for plotting
        - descripcion: Detailed description
        
    Example:
        >>> from iniamet.utils import get_variable_info, VAR_TEMPERATURA_MEDIA
        >>> info = get_variable_info(VAR_TEMPERATURA_MEDIA)
        >>> print(info['nombre'])
        'Temperatura del Aire Media'
        >>> print(info['unidad'])
        '°C'
    """
    if variable_id not in VARIABLE_INFO:
        return {
            'nombre': f'Variable {variable_id}',
            'unidad': '',
            'color': 'gray',
            'descripcion': f'Variable desconocida (ID: {variable_id})'
        }
    return VARIABLE_INFO[variable_id]


def is_valid_variable_id(variable_id: int) -> bool:
    """
    Check if a variable ID is valid/known.
    
    Args:
        variable_id: Variable ID to validate
        
    Returns:
        True if variable ID exists in VARIABLE_INFO
        
    Example:
        >>> from iniamet.utils import is_valid_variable_id, VAR_TEMPERATURA_MEDIA
        >>> is_valid_variable_id(VAR_TEMPERATURA_MEDIA)
        True
        >>> is_valid_variable_id(9999)
        False
    """
    return variable_id in VARIABLE_INFO


def list_all_variables() -> 'pd.DataFrame':
    """
    Get a DataFrame with all known variables.
    
    Returns:
        DataFrame with columns: variable_id, nombre, unidad, descripcion
        
    Example:
        >>> from iniamet.utils import list_all_variables
        >>> vars_df = list_all_variables()\n        >>> print(vars_df[['variable_id', 'nombre', 'unidad']])
    """
    import pandas as pd
    
    data = []
    for var_id, info in VARIABLE_INFO.items():
        data.append({
            'variable_id': var_id,
            'nombre': info['nombre'],
            'unidad': info['unidad'],
            'descripcion': info['descripcion']
        })
    
    return pd.DataFrame(data).sort_values('variable_id').reset_index(drop=True)


def get_variable_id_by_name(name: str) -> Optional[int]:
    """
    Find variable ID by searching for a name (fuzzy match).
    
    Args:
        name: Variable name or partial name (e.g., "temperatura", "precipitacion")
        
    Returns:
        Variable ID if found, None otherwise
        
    Example:
        >>> from iniamet.utils import get_variable_id_by_name
        >>> get_variable_id_by_name("temperatura")
        2002
        >>> get_variable_id_by_name("precipitacion")
        2001
    """
    name_normalized = normalize_text(name)
    
    # Try exact match first
    for var_id, info in VARIABLE_INFO.items():
        if normalize_text(info['nombre']) == name_normalized:
            return var_id
    
    # Try partial match
    for var_id, info in VARIABLE_INFO.items():
        if name_normalized in normalize_text(info['nombre']):
            return var_id
    
    return None


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison (lowercase + remove accents).
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
        
    Example:
        >>> normalize_text("Precipitación")
        'precipitacion'
    """
    text = text.lower()
    
    # Remove Spanish accents
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def parse_date(date: Union[str, datetime, date]) -> datetime:
    """
    Parse date from string, datetime, or date.
    
    Args:
        date: Date as string (YYYY-MM-DD), datetime object, or date object
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    # Handle different input types
    if isinstance(date, str):
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date}. Expected YYYY-MM-DD"
            )
    elif isinstance(date, datetime):
        return date
    elif isinstance(date, date):
        return datetime.combine(date, datetime.min.time())
    else:
        raise TypeError(f"Expected str, datetime, or date, got {type(date)}")


def format_station_code(code: str) -> str:
    """
    Normalize station code format.
    
    Args:
        code: Station code
        
    Returns:
        Normalized code (uppercase)
    """
    return code.strip().upper()


def get_region_name(code: str) -> str:
    """
    Get region name from code or name.

    Args:
        code: Region code (e.g., "R16") or region name (e.g., "Ñuble")

    Returns:
        Region name (e.g., "Ñuble")

    Raises:
        ValueError: If code/name is invalid
    """
    code = code.upper().strip()

    # If it's already a region code (starts with R), return the name
    if code in REGION_MAP:
        return REGION_MAP[code]

    # If it's a region name, find the corresponding code
    for region_code, region_name in REGION_MAP.items():
        if region_name.upper() == code:
            return region_name

    # Try to find partial matches (e.g., "COQUIMBO" should match "Coquimbo")
    for region_code, region_name in REGION_MAP.items():
        if code in region_name.upper() or region_name.upper() in code:
            return region_name

    # If not found, return the input as-is (graceful degradation)
    return code.title()


def get_region_code(name: str) -> Optional[str]:
    """
    Get region code from name.
    
    Args:
        name: Region name (e.g., "Ñuble") or code (e.g., "R16")
        
    Returns:
        Region code (e.g., "R16") or None if invalid
    """
    # If already a code, return it
    if name.upper() in REGION_MAP:
        return name.upper()
    
    name_normalized = normalize_text(name)
    
    for code, region_name in REGION_MAP.items():
        if normalize_text(region_name) == name_normalized:
            return code
    
    return None
