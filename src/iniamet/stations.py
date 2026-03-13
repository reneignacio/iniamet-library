"""Módulo de gestión de estaciones.

Maneja consultas, filtrado y validación de variables de estaciones
agrometeorológicas.
"""

import logging
from typing import Optional, List, Union
import pandas as pd

from .api_client import APIClient
from .cache import CacheManager
from .utils import normalize_text, normalize_region, normalize_regions, REGION_MAP

logger = logging.getLogger(__name__)


class StationManager:
    """Gestiona el catálogo de estaciones y sus consultas.

    Se utiliza internamente por :class:`~iniamet.client.INIAClient`.
    Normalmente no se instancia directamente.
    """
    
    def __init__(self, api: APIClient, cache: Optional[CacheManager] = None):
        """Inicializa el gestor de estaciones.

        Args:
            api: Instancia de :class:`~iniamet.api_client.APIClient`.
            cache: Instancia de :class:`~iniamet.cache.CacheManager` (opcional).
        """
        self.api = api
        self.cache = cache
        self._stations_cache: Optional[pd.DataFrame] = None
    
    def get_stations(
        self,
        region: Optional[Union[str, List[str]]] = None,
        station_type: Optional[str] = None,
        force_update: bool = False
    ) -> pd.DataFrame:
        """Obtiene estaciones con filtrado opcional.

        Args:
            region: Una o más regiones. Acepta:
                ``"R16"``, ``"Ñuble"``, ``"16"`` o
                ``["R16", "R08"]`` para varias.
            station_type: Prefijo de tipo de estación (ej. ``"INIA"``, ``"DMC"``).
            force_update: Forzar descarga desde la API (ignora caché).

        Returns:
            ``pd.DataFrame`` con columnas: ``codigo``, ``nombre``, ``region``,
            ``comuna``, ``latitud``, ``longitud``, ``elevacion``, ``tipo``,
            ``primera_lectura``.

        Example:
            >>> sm.get_stations(region="Ñuble", station_type="INIA")
        """
        # Check memory cache
        if self._stations_cache is not None and not force_update:
            logger.info("Using cached stations from memory")
            df = self._stations_cache.copy()
        else:
            # Try disk cache
            if self.cache and not force_update:
                df = self.cache.get_stations()
                if df is not None:
                    logger.info("Using cached stations from disk")
                    self._stations_cache = df.copy()
                    return self._filter_stations(df, region, station_type)
            
            # Fetch from API
            logger.info("Fetching stations from API...")
            data = self.api.get_stations()
            
            if not data:
                return pd.DataFrame()
            
            # Normalize station data
            stations = []
            for item in data:
                # Extract station type from code (e.g., "INIA" from "INIA-47")
                codigo = item.get('identificador', '')
                tipo = codigo.split('-')[0] if '-' in codigo else 'OTHER'
                
                stations.append({
                    'codigo': codigo,
                    'nombre': item.get('nombre', ''),
                    'region': item.get('region', ''),
                    'comuna': item.get('comuna', ''),
                    'latitud': item.get('latitud'),
                    'longitud': item.get('longitud'),
                    'elevacion': item.get('elevacion'),
                    'tipo': tipo,
                    'primera_lectura': item.get('primer_dato', '')
                })
            
            df = pd.DataFrame(stations)
            
            # Save to caches
            if self.cache:
                self.cache.save_stations(df)
            self._stations_cache = df.copy()
            
            logger.info(f"Retrieved {len(df)} stations")
        
        return self._filter_stations(df, region, station_type)
    
    def _filter_stations(
        self,
        df: pd.DataFrame,
        region: Optional[Union[str, List[str]]] = None,
        station_type: Optional[str] = None
    ) -> pd.DataFrame:
        """Aplica filtros al DataFrame de estaciones."""
        if df.empty:
            return df
        
        result = df.copy()
        
        # Filter by region (accepts single or list, any format)
        if region:
            try:
                region_names = normalize_regions(region)
                result = result[result['region'].isin(region_names)]
            except ValueError as e:
                logger.warning(f"Region error: {e}")
                return pd.DataFrame()
        
        # Filter by station type
        if station_type:
            result = result[
                result['tipo'].str.upper() == station_type.upper()
            ]
        
        logger.info(f"Filtered to {len(result)} stations")
        return result.reset_index(drop=True)
    
    def get_variables(
        self,
        station: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """Obtiene las variables disponibles para una estación.

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            force_update: Forzar descarga desde la API.

        Returns:
            ``pd.DataFrame`` con columnas: ``variable_id``, ``nombre``, ``unidad``.

        Example:
            >>> variables = sm.get_variables("INIA-47")
        """
        # Check cache
        if self.cache and not force_update:
            df = self.cache.get_variables(station)
            if df is not None:
                logger.info(f"Using cached variables for {station}")
                return df
        
        # Fetch from API
        logger.info(f"Fetching variables for {station}...")
        data = self.api.get_variables(station)
        
        if not data:
            return pd.DataFrame()
        
        # Normalize variable data
        variables = []
        for item in data:
            variables.append({
                'variable_id': item.get('identificador'),
                'nombre': item.get('nombre', ''),
                'unidad': item.get('unidad', '')
            })
        
        df = pd.DataFrame(variables)
        
        # Save to cache
        if self.cache:
            self.cache.save_variables(station, df)
        
        logger.info(f"Retrieved {len(df)} variables for {station}")
        return df
    
    def validate_station_variable(
        self,
        station: str,
        variable: Union[int, str]
    ) -> bool:
        """Verifica si una variable existe para una estación.

        Acepta búsqueda por ID numérico o por nombre (búsqueda difusa).

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            variable: ID de la variable (``int``) o nombre (``str``).

        Returns:
            ``True`` si la variable está disponible.

        Example:
            >>> sm.validate_station_variable("INIA-47", 2002)
            True
            >>> sm.validate_station_variable("INIA-47", "temperatura")
            True
        """
        df_vars = self.get_variables(station)
        
        if df_vars.empty:
            return False
        
        # Check by ID
        if isinstance(variable, int) or variable.isdigit():
            var_id = int(variable)
            return var_id in df_vars['variable_id'].values
        
        # Check by name (fuzzy match)
        variable_lower = normalize_text(str(variable))
        for nombre in df_vars['nombre']:
            if variable_lower in normalize_text(nombre):
                return True
        
        return False
    
    def find_variable_id(
        self,
        station: str,
        variable_name: str
    ) -> Optional[int]:
        """Busca el ID de una variable por nombre (búsqueda difusa).

        Args:
            station: Código de la estación.
            variable_name: Nombre o parte del nombre de la variable
                (ej. ``"temperatura"``, ``"precipitacion"``).

        Returns:
            ID de la variable si se encuentra, ``None`` en caso contrario.

        Example:
            >>> sm.find_variable_id("INIA-47", "temperatura")
            2002
        """
        df_vars = self.get_variables(station)
        
        if df_vars.empty:
            return None
        
        variable_lower = normalize_text(variable_name)
        
        for _, row in df_vars.iterrows():
            if variable_lower in normalize_text(row['nombre']):
                return int(row['variable_id'])
        
        return None
