"""Módulo de descarga regional.

Simplifica la descarga masiva de datos climáticos para una región
completa, consolidando múltiples estaciones y variables en un
único DataFrame.
"""

import logging
from typing import Optional, List, Union
from datetime import datetime
import pandas as pd

from .client import INIAClient
from .utils import (
    VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION, VAR_HUMEDAD_RELATIVA,
    VAR_VIENTO_VELOCIDAD_MEDIA, VAR_VIENTO_VELOCIDAD_MAXIMA, VAR_VIENTO_DIRECCION,
    VAR_RADIACION_MEDIA, VAR_PRESION_ATMOSFERICA,
    VAR_TEMPERATURA_SUELO_10CM, VAR_TEMPERATURA_SUPERFICIE, VAR_BATERIA_VOLTAJE
)

logger = logging.getLogger(__name__)


class RegionalDownloader:
    """Descargador de datos climáticos a nivel regional.

    Descarga y consolida datos de todas las estaciones de una región
    en un solo DataFrame.

    Attributes:
        VARIABLE_MAPPING: Diccionario que mapea nombres en inglés a IDs
            de variable. Claves disponibles: ``'temperature'``,
            ``'precipitation'``, ``'humidity'``, ``'wind_speed'``,
            ``'wind_speed_max'``, ``'wind_direction'``, ``'radiation'``,
            ``'pressure'``, ``'soil_temperature'``,
            ``'surface_temperature'``, ``'battery_voltage'``.
        stations: ``pd.DataFrame`` con las estaciones de la región
            (se carga automáticamente al inicializar).

    Example:
        >>> from iniamet import RegionalDownloader
        >>> rd = RegionalDownloader(region="Ñuble")
        >>> df = rd.download_climate_data(
        ...     "2025-01-01", "2025-01-31",
        ...     variables=["temperature", "precipitation"]
        ... )
        >>> rd.save_to_csv(df)
    """
    
    # Common variable mappings - Use string names or direct variable ID constants
    VARIABLE_MAPPING = {
        'temperature': VAR_TEMPERATURA_MEDIA,
        'precipitation': VAR_PRECIPITACION,
        'humidity': VAR_HUMEDAD_RELATIVA,
        'wind_speed': VAR_VIENTO_VELOCIDAD_MEDIA,
        'wind_speed_max': VAR_VIENTO_VELOCIDAD_MAXIMA,
        'wind_direction': VAR_VIENTO_DIRECCION,
        'radiation': VAR_RADIACION_MEDIA,
        'pressure': VAR_PRESION_ATMOSFERICA,
        'soil_temperature': VAR_TEMPERATURA_SUELO_10CM,
        'surface_temperature': VAR_TEMPERATURA_SUPERFICIE,
        'battery_voltage': VAR_BATERIA_VOLTAJE,
    }
    
    def __init__(
        self,
        region: str,
        client: Optional[INIAClient] = None
    ):
        """Inicializa el descargador regional.

        Al crear la instancia se descargan automáticamente las estaciones
        de la región indicada.

        Args:
            region: Código de región (ej. ``"R16"``) o nombre
                (ej. ``"Ñuble"``).
            client: Instancia de :class:`~iniamet.client.INIAClient`.
                Si es ``None`` se crea una nueva automáticamente.
        """
        self.region = region
        self.client = client or INIAClient()
        
        # Get stations for region
        self.stations = self.client.get_stations(region=region)
        
        if self.stations.empty:
            logger.warning(f"No stations found for region {region}")
        else:
            logger.info(f"Found {len(self.stations)} stations in region {region}")
    
    def download_climate_data(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        variables: Optional[List[str]] = None,
        aggregation: str = 'daily',
        station_filter: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Descarga y consolida datos climáticos de la región.

        Args:
            start_date: Fecha inicio (``"YYYY-MM-DD"`` o ``datetime``).
            end_date: Fecha fin (``"YYYY-MM-DD"`` o ``datetime``).
            variables: Lista de nombres de variables en inglés
                (ej. ``["temperature", "precipitation"]``).
                Si es ``None`` se descargan temperatura y precipitación.
                Ver ``VARIABLE_MAPPING`` para la lista completa.
            aggregation: Agregación temporal:
                ``"daily"`` (por defecto), ``"raw"``, ``"W"``, ``"M"``.
            station_filter: Lista opcional de códigos de estación
                específicos a descargar.

        Returns:
            ``pd.DataFrame`` consolidado con columnas: ``estacion_codigo``,
            ``estacion_nombre``, ``region``, ``latitud``, ``longitud``,
            ``elevacion``, ``tiempo``, ``valor``, etc.

        Example:
            >>> df = rd.download_climate_data(
            ...     "2025-01-01", "2025-01-31",
            ...     variables=["temperature", "precipitation"],
            ...     aggregation="daily"
            ... )
        """
        # Default variables
        if variables is None:
            variables = ['temperature', 'precipitation']
        
        # Resolve variable IDs
        var_ids = []
        for var in variables:
            if var.lower() in self.VARIABLE_MAPPING:
                var_ids.append(self.VARIABLE_MAPPING[var.lower()])
            else:
                logger.warning(f"Unknown variable: {var}")
        
        if not var_ids:
            logger.error("No valid variables specified")
            return pd.DataFrame()
        
        # Filter stations if requested
        stations_to_use = self.stations.copy()
        if station_filter:
            stations_to_use = stations_to_use[
                stations_to_use['codigo'].isin(station_filter)
            ]
        
        if stations_to_use.empty:
            logger.error("No stations to download")
            return pd.DataFrame()
        
        # Download data for each station
        all_data = []
        
        for idx, station_row in stations_to_use.iterrows():
            station_code = station_row['codigo']
            station_name = station_row['nombre']
            
            logger.info(f"[{idx+1}/{len(stations_to_use)}] {station_code} - {station_name}")
            
            station_data = {
                'estacion_codigo': station_code,
                'estacion_nombre': station_name,
                'region': station_row['region'],
                'latitud': station_row['latitud'],
                'longitud': station_row['longitud'],
                'elevacion': station_row['elevacion']
            }
            
            # Download each variable
            for var_id in var_ids:
                try:
                    # Convert aggregation format
                    agg_rule = None
                    if aggregation and aggregation != 'raw':
                        if aggregation == 'daily':
                            agg_rule = 'D'
                        else:
                            agg_rule = aggregation
                    
                    # Use client's built-in aggregation
                    df = self.client.get_data(
                        station=station_code,
                        variable=var_id,
                        start_date=start_date,
                        end_date=end_date,
                        aggregation=agg_rule
                    )
                    
                    if df.empty:
                        logger.warning(f"  No data for variable {var_id}")
                        continue
                    
                    # Add variable columns to station data
                    for col in df.columns:
                        if col != 'tiempo':
                            station_data[col] = df[col].values
                    
                    if 'tiempo' not in station_data:
                        station_data['tiempo'] = df['tiempo'].values
                    
                    logger.info(f"  ✓ Variable {var_id}: {len(df)} records")
                    
                except Exception as e:
                    logger.error(f"  ✗ Variable {var_id}: {e}")
                    continue
            
            # Create DataFrame for this station
            if 'tiempo' in station_data:
                df_station = pd.DataFrame({
                    'tiempo': station_data['tiempo']
                })
                
                for key, value in station_data.items():
                    if key != 'tiempo':
                        if isinstance(value, (list, pd.Series)):
                            df_station[key] = value
                        else:
                            df_station[key] = value
                
                all_data.append(df_station)
        
        # Consolidate all stations
        if not all_data:
            logger.error("No data downloaded")
            return pd.DataFrame()
        
        df_final = pd.concat(all_data, ignore_index=True)
        df_final = df_final.sort_values(['estacion_codigo', 'tiempo'])
        df_final = df_final.reset_index(drop=True)
        
        logger.info(f"Download complete: {len(df_final)} total records")
        return df_final
    
    def _aggregate_daily(self, df: pd.DataFrame, var_id: int) -> pd.DataFrame:
        """Agrega datos a resolución diaria según el tipo de variable."""
        if df.empty:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        # Temperature: compute min/max/mean
        if var_id == 2002:  # Temperature
            df_daily = df.resample('D').agg({
                'valor': ['mean', 'min', 'max']
            })
            df_daily.columns = ['tmedia', 'tmin', 'tmax']
        
        # Precipitation: sum
        elif var_id == 2001:  # Precipitation
            df_daily = df.resample('D').sum()
            df_daily.columns = ['pp_acum']
        
        # Others: mean
        else:
            df_daily = df.resample('D').mean()
            df_daily.columns = [f'var_{var_id}']
        
        df_daily = df_daily.reset_index()
        return df_daily
    
    def _aggregate_custom(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Aplica una regla de agregación personalizada."""
        if df.empty:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        df_agg = df.resample(rule).mean()
        df_agg = df_agg.reset_index()
        return df_agg
    
    def save_to_csv(
        self,
        df: pd.DataFrame,
        filename: Optional[str] = None
    ) -> str:
        """Guarda un DataFrame en archivo CSV.

        Args:
            df: DataFrame a guardar.
            filename: Nombre del archivo de salida. Si es ``None`` se
                genera automáticamente (ej. ``clima_r16.csv``).

        Returns:
            Ruta del archivo guardado.

        Example:
            >>> ruta = rd.save_to_csv(df, "datos_nuble.csv")
        """
        if filename is None:
            region_code = self.region if self.region.startswith('R') else 'region'
            filename = f"clima_{region_code.lower()}.csv"
        
        df.to_csv(filename, index=False)
        logger.info(f"Saved to {filename} ({len(df)} records)")
        
        return filename
