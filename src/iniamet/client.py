"""Cliente principal para datos agrometeorológicos de INIA Chile.

Este módulo es el punto de entrada principal de la librería.
"""

import logging
from typing import Optional, List, Union, Dict
from datetime import datetime
import pandas as pd

from .api_client import APIClient
from .stations import StationManager
from .data import DataDownloader
from .cache import CacheManager

logger = logging.getLogger(__name__)


class INIAClient:
    """Cliente de alto nivel para acceder a datos de estaciones agrometeorológicas de INIA.

    Clase principal de la librería. Provee métodos simples para consultar
    estaciones, variables y descargar series de tiempo.

    Args:
        api_key: Clave de la API de INIA Agromet. Si no se entrega, se busca
            en la variable de entorno ``INIA_API_KEY`` o en ``~/.iniamet/config``.
        cache: Activar/desactivar el caché local en disco (por defecto ``True``).
        cache_dir: Directorio donde se almacena el caché (por defecto ``./iniamet_cache``).

    Example:
        >>> from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
        >>> client = INIAClient(api_key="tu_key")
        >>> estaciones = client.get_stations(region="Ñuble")
        >>> temp = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
        ...                        "2025-01-01", "2025-01-31",
        ...                        aggregation="diario")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache: bool = True,
        cache_dir: str = "./iniamet_cache"
    ):
        """Inicializa el cliente INIA.

        Args:
            api_key: Clave de API. Si es ``None``, se busca en variable de entorno
                o archivo de configuración.
            cache: Activar caché en disco (por defecto ``True``).
            cache_dir: Ruta del directorio de caché.
        """
        self.api = APIClient(api_key=api_key)
        self.cache_manager = CacheManager(cache_dir=cache_dir) if cache else None
        self.station_manager = StationManager(self.api, self.cache_manager)
        self.data_downloader = DataDownloader(self.api, self.cache_manager)
        
        logger.info("INIA Client initialized")
    
    def get_stations(
        self,
        region: Optional[Union[str, List[str]]] = None,
        station_type: Optional[str] = None,
        force_update: bool = False
    ) -> pd.DataFrame:
        """Obtiene la lista de estaciones disponibles.

        Args:
            region: Una o más regiones. Acepta cualquier formato:
                ``"R16"``, ``"Ñuble"``, ``"16"`` o una lista
                ``["R16", "R08"]``.
            station_type: Filtrar por tipo de estación (ej. ``"INIA"``, ``"DMC"``).
            force_update: Forzar actualización desde la API (ignora caché).

        Returns:
            ``pd.DataFrame`` con columnas: ``codigo``, ``nombre``, ``region``,
            ``comuna``, ``latitud``, ``longitud``, ``elevacion``, ``tipo``,
            ``primera_lectura``.

        Examples:
            >>> client.get_stations(region="Ñuble")
            >>> client.get_stations(region=["R16", "R08"], station_type="INIA")
        """
        return self.station_manager.get_stations(
            region=region,
            station_type=station_type,
            force_update=force_update
        )
    
    def get_variables(
        self,
        station: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """Obtiene las variables disponibles para una estación.

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            force_update: Forzar actualización desde la API.

        Returns:
            ``pd.DataFrame`` con columnas: ``variable_id``, ``nombre``, ``unidad``.

        Example:
            >>> variables = client.get_variables("INIA-47")
            >>> print(variables[['variable_id', 'nombre', 'unidad']])
        """
        return self.station_manager.get_variables(
            station=station,
            force_update=force_update
        )
    
    def get_data(
        self,
        station: str,
        variable: Union[int, str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True,
        aggregation: Optional[str] = None
    ) -> pd.DataFrame:
        """Descarga datos de serie de tiempo para una estación y variable.

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            variable: ID de la variable (``int``) o constante.
                Usa las constantes: ``VAR_TEMPERATURA_MEDIA``,
                ``VAR_PRECIPITACION``, etc.
            start_date: Fecha inicio (``"YYYY-MM-DD"`` o ``datetime``).
            end_date: Fecha fin (``"YYYY-MM-DD"`` o ``datetime``).
            use_cache: Usar datos en caché si están disponibles.
            aggregation: Agregación temporal opcional:

                - ``None`` / ``"raw"`` / ``"crudo"``: datos cada 15 min (por defecto)
                - ``"horario"`` / ``"hourly"`` / ``"H"``: horario
                - ``"diario"`` / ``"daily"`` / ``"D"``: diario
                - ``"semanal"`` / ``"weekly"`` / ``"W"``: semanal
                - ``"mensual"`` / ``"monthly"`` / ``"M"``: mensual

        Returns:
            ``pd.DataFrame`` con columnas ``tiempo`` y ``valor``.
            Para temperatura con agregación diaria se agregan
            ``valor_min``, ``valor_max`` y ``valor_media``.
            Para precipitación se calcula la suma.

        Example:
            >>> from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
            >>> client = INIAClient(api_key="...")
            >>> temp = client.get_data(
            ...     "INIA-47", VAR_TEMPERATURA_MEDIA,
            ...     "2025-01-01", "2025-01-31",
            ...     aggregation="diario"
            ... )
        """
        return self.data_downloader.get_data(
            station=station,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            use_cache=use_cache,
            aggregation=aggregation
        )
    
    def bulk_download(
        self,
        stations: List[str],
        variables: List[Union[int, str]],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        delay: float = 0.5
    ) -> Dict[str, pd.DataFrame]:
        """Descarga datos de múltiples estaciones y variables.

        Args:
            stations: Lista de códigos de estación
                (ej. ``["INIA-47", "INIA-139"]``).
            variables: Lista de IDs de variable
                (ej. ``[VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION]``).
            start_date: Fecha inicio.
            end_date: Fecha fin.
            delay: Segundos de espera entre peticiones (evita rate-limiting).

        Returns:
            ``Dict[str, pd.DataFrame]`` donde la clave es
            ``"estacion_variable"`` (ej. ``"INIA-47_2002"``).

        Example:
            >>> datos = client.bulk_download(
            ...     stations=["INIA-47", "INIA-139"],
            ...     variables=[VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION],
            ...     start_date="2025-01-01",
            ...     end_date="2025-01-31"
            ... )
        """
        return self.data_downloader.bulk_download(
            stations=stations,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
            delay=delay
        )
    
    def validate_station_variable(
        self,
        station: str,
        variable: Union[int, str]
    ) -> bool:
        """Verifica si una variable está disponible para una estación.

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            variable: ID de la variable (``int``) o nombre (``str``).

        Returns:
            ``True`` si la variable existe para esa estación.

        Example:
            >>> client.validate_station_variable("INIA-47", VAR_TEMPERATURA_MEDIA)
            True
        """
        return self.station_manager.validate_station_variable(
            station=station,
            variable=variable
        )
    
    def close(self):
        """Cierra la conexión HTTP y libera recursos."""
        self.api.close()
        logger.info("INIA Client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
