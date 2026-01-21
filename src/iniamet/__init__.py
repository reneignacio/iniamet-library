"""
INIAMET - Chilean INIA Agrometeorological Data Library

An unofficial, high-level Python library for accessing Chilean INIA 
agrometeorological station data.

DISCLAIMER: This library is NOT officially affiliated with, endorsed by, 
or maintained by INIA (Instituto de Investigaciones Agropecuarias). 
It accesses publicly available data from INIA's agrometeorological API.

Example usage:
    >>> from iniamet import INIAClient
    >>> client = INIAClient()
    >>> stations = client.get_stations(region="R16")
    >>> print(len(stations))
    
    # Quality control
    >>> from iniamet.qc import apply_quality_control
    >>> clean_data = apply_quality_control(df, 'temperatura')
    
    # Visualization
    >>> from iniamet.visualization import quick_temp_map
    >>> mapa = quick_temp_map(client, region='Ñuble', date='2025-10-12')
"""

__version__ = "0.2.0"
__author__ = "INIA Climate Data Team"
__license__ = "MIT"

from .client import INIAClient
from .stations import StationManager
from .data import DataDownloader
from .regional import RegionalDownloader
from .qc import QualityControl, apply_quality_control, get_qc_report
from .utils import (
    get_region_name, 
    get_variable_info, 
    list_all_variables,
    get_variable_id_by_name,
    is_valid_variable_id,
    REGION_MAP, 
    VARIABLE_INFO,
    # Variable ID constants for easy access
    VAR_PRECIPITACION,
    VAR_TEMPERATURA_MEDIA,
    VAR_TEMPERATURA_SUELO_10CM,
    VAR_TEMPERATURA_SUPERFICIE,
    VAR_HUMEDAD_RELATIVA,
    VAR_VIENTO_DIRECCION,
    VAR_VIENTO_VELOCIDAD_MEDIA,
    VAR_VIENTO_VELOCIDAD_MAXIMA,
    VAR_RADIACION_MEDIA,
    VAR_PRESION_ATMOSFERICA,
    VAR_BATERIA_VOLTAJE
)

# Import visualization only if IPython is available (optional dependency)
try:
    from .visualization import plot_temperature_map, plot_station_map, quick_temp_map
    _HAS_VISUALIZATION = True
except ImportError:
    _HAS_VISUALIZATION = False
    plot_temperature_map = None
    plot_station_map = None
    quick_temp_map = None

__all__ = [
    "INIAClient",
    "StationManager",
    "DataDownloader",
    "RegionalDownloader",
    "QualityControl",
    "apply_quality_control",
    "get_qc_report",
    "plot_temperature_map",
    "plot_station_map",
    "quick_temp_map",
    "get_region_name",
    "get_variable_info",
    "list_all_variables",
    "get_variable_id_by_name",
    "is_valid_variable_id",
    "REGION_MAP",
    "VARIABLE_INFO",
    # Variable ID constants
    "VAR_PRECIPITACION",
    "VAR_TEMPERATURA_MEDIA",
    "VAR_TEMPERATURA_SUELO_10CM",
    "VAR_TEMPERATURA_SUPERFICIE",
    "VAR_HUMEDAD_RELATIVA",
    "VAR_VIENTO_DIRECCION",
    "VAR_VIENTO_VELOCIDAD_MEDIA",
    "VAR_VIENTO_VELOCIDAD_MAXIMA",
    "VAR_RADIACION_MEDIA",
    "VAR_PRESION_ATMOSFERICA",
    "VAR_BATERIA_VOLTAJE",
]
