"""Módulo de descarga de datos.

Maneja la descarga de series de tiempo con soporte de caché
y agregación temporal.
"""

import logging
import time
from typing import Optional, List, Union, Dict
from datetime import datetime
import pandas as pd

from .api_client import APIClient
from .cache import CacheManager
from .utils import parse_date

logger = logging.getLogger(__name__)


class DataDownloader:
    """Descarga y procesa datos desde la API de INIA.

    Se utiliza internamente por :class:`~iniamet.client.INIAClient`.
    Normalmente no se instancia directamente.
    """
    
    def __init__(self, api: APIClient, cache: Optional[CacheManager] = None):
        """Inicializa el descargador de datos.

        Args:
            api: Instancia de :class:`~iniamet.api_client.APIClient`.
            cache: Instancia de :class:`~iniamet.cache.CacheManager` (opcional).
        """
        self.api = api
        self.cache = cache
    
    def get_data(
        self,
        station: str,
        variable: Union[int, str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True,
        aggregation: Optional[str] = None
    ) -> pd.DataFrame:
        """Descarga datos de serie de tiempo con agregación temporal opcional.

        Args:
            station: Código de la estación (ej. ``"INIA-47"``).
            variable: ID de la variable (ej. ``2002`` para temperatura)
                o constante (ej. ``VAR_TEMPERATURA_MEDIA``).
            start_date: Fecha inicio (``"YYYY-MM-DD"`` o ``datetime``).
            end_date: Fecha fin (``"YYYY-MM-DD"`` o ``datetime``).
            use_cache: Usar datos en caché si están disponibles.
            aggregation: Agregación temporal. Alias aceptados:

                - ``None`` / ``"raw"`` / ``"crudo"``: cada 15 min (por defecto)
                - ``"horario"`` / ``"hourly"`` / ``"H"`` / ``"h"``: horario
                - ``"diario"`` / ``"daily"`` / ``"D"``: diario
                - ``"semanal"`` / ``"weekly"`` / ``"W"``: semanal
                - ``"mensual"`` / ``"monthly"`` / ``"M"``: mensual

        Returns:
            ``pd.DataFrame`` con columnas ``tiempo`` y ``valor``.
            Para temperatura agregada se agregan ``valor_min``,
            ``valor_max`` y ``valor_media``.
            Para precipitación se calcula la suma acumulada.

        Raises:
            ValueError: Si las fechas tienen formato inválido.

        Example:
            >>> df = downloader.get_data(
            ...     "INIA-47", VAR_TEMPERATURA_MEDIA,
            ...     "2025-01-01", "2025-01-31",
            ...     aggregation="diario"
            ... )
        """
        # Normalize aggregation aliases based on pandas version
        # pandas >= 2.2.0 deprecated 'M' and 'H' in favor of 'ME' and 'h'
        pd_version = pd.__version__.split('.')
        pd_major_minor = float(f"{pd_version[0]}.{pd_version[1]}")
        
        c_month = 'ME' if pd_major_minor >= 2.2 else 'M'
        c_hour = 'h' if pd_major_minor >= 2.2 else 'H'
        
        _AGG_ALIASES = {
            'daily': 'D', 'diario': 'D', 'd': 'D',
            'hourly': c_hour, 'horario': c_hour, 'h': c_hour,
            'weekly': 'W', 'semanal': 'W', 'w': 'W',
            'monthly': c_month, 'mensual': c_month, 'm': c_month, 'me': c_month,
            'raw': None, 'crudo': None,
        }
        if aggregation and aggregation.lower() in _AGG_ALIASES:
            aggregation = _AGG_ALIASES[aggregation.lower()]
        
        # Parse dates
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
        
        # Convert variable to string
        var_str = str(variable)
        
        # Check cache
        if self.cache and use_cache:
            df_cached = self.cache.get_data(station, var_str, start_dt, end_dt)
            if df_cached is not None and not df_cached.empty:
                logger.info(
                    f"Using cached data for {station}/{var_str} "
                    f"({len(df_cached)} records)"
                )
                # Apply aggregation to cached data if requested
                if aggregation and aggregation != 'raw':
                    return self._apply_aggregation(
                        df_cached, int(var_str), aggregation
                    )
                return df_cached
        
        # Download from API
        logger.info(f"Downloading data for {station}/{var_str}...")
        
        data = self.api.get_data(
            station=station,
            variable=var_str,
            start_date=start_dt.strftime('%Y-%m-%d'),
            end_date=end_dt.strftime('%Y-%m-%d')
        )
        
        if not data:
            logger.warning(f"No data found for {station}/{var_str}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Parse tiempo column
        if 'tiempo' in df.columns:
            df['tiempo'] = pd.to_datetime(df['tiempo'])
        
        # Parse valor column
        if 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        # Sort by time
        if not df.empty:
            df = df.sort_values('tiempo').reset_index(drop=True)
        
        # Apply aggregation if requested
        if aggregation and aggregation != 'raw' and not df.empty:
            df = self._apply_aggregation(df, int(var_str), aggregation)
        
        # Save to cache (raw data only)
        if self.cache and not df.empty and (aggregation is None or aggregation == 'raw'):
            self.cache.save_data(station, var_str, df)
        
        logger.info(f"Downloaded {len(df)} records")
        return df
    
    def _apply_aggregation(
        self,
        df: pd.DataFrame,
        variable_id: int,
        rule: str
    ) -> pd.DataFrame:
        """Aplica agregación temporal a datos de serie de tiempo.

        - **Temperatura**: calcula min, max y media.
        - **Precipitación**: calcula suma acumulada.
        - **Otras variables**: calcula promedio.

        Args:
            df: DataFrame con columnas ``tiempo`` y ``valor``.
            variable_id: ID de la variable (determina el método de agregación).
            rule: Regla de resample de pandas (ej. ``"D"``, ``"W"``, ``"ME"``).

        Returns:
            ``pd.DataFrame`` agregado.
        """
        if df.empty:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        # Import constants to avoid magic numbers
        from .utils import (
            VAR_TEMPERATURA_MEDIA, VAR_TEMPERATURA_SUELO_10CM, 
            VAR_TEMPERATURA_SUPERFICIE, VAR_PRECIPITACION
        )
        
        # Temperature variables: compute min/max/mean
        if variable_id in [VAR_TEMPERATURA_MEDIA, VAR_TEMPERATURA_SUELO_10CM, 
                          VAR_TEMPERATURA_SUPERFICIE]:
            df_agg = df.resample(rule).agg({
                'valor': ['mean', 'min', 'max']
            })
            df_agg.columns = ['valor_media', 'valor_min', 'valor_max']
            # Keep 'valor' as the mean for backwards compatibility
            df_agg['valor'] = df_agg['valor_media']
        
        # Precipitation: sum
        elif variable_id == VAR_PRECIPITACION:
            df_agg = df.resample(rule).sum()
        
        # Others: mean
        else:
            df_agg = df.resample(rule).mean()
        
        df_agg = df_agg.reset_index()
        return df_agg
    
    def bulk_download(
        self,
        stations: List[str],
        variables: List[Union[int, str]],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        delay: float = 0.5
    ) -> Dict[str, pd.DataFrame]:
        """Descarga datos de múltiples estaciones y variables.

        Ejecuta las descargas secuencialmente con una pausa entre cada
        petición para evitar rate-limiting de la API.

        Args:
            stations: Lista de códigos de estación.
            variables: Lista de IDs de variable.
            start_date: Fecha inicio.
            end_date: Fecha fin.
            delay: Segundos de espera entre peticiones (por defecto ``0.5``).

        Returns:
            ``Dict[str, pd.DataFrame]`` donde la clave es
            ``"estacion_variable"`` (ej. ``"INIA-47_2002"``).

        Example:
            >>> datos = downloader.bulk_download(
            ...     ["INIA-47", "INIA-139"],
            ...     [VAR_TEMPERATURA_MEDIA],
            ...     "2025-01-01", "2025-01-31"
            ... )
        """
        results = {}
        total = len(stations) * len(variables)
        current = 0
        
        logger.info(f"Bulk download: {len(stations)} stations × {len(variables)} variables = {total} tasks")
        
        for station in stations:
            for variable in variables:
                current += 1
                key = f"{station}_{variable}"
                
                logger.info(f"[{current}/{total}] Downloading {key}...")
                
                try:
                    df = self.get_data(
                        station=station,
                        variable=variable,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if not df.empty:
                        results[key] = df
                        logger.info(f"  ✓ {key}: {len(df)} records")
                    else:
                        logger.warning(f"  ⚠ {key}: No data")
                    
                    # Rate limiting
                    if current < total:
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"  ✗ {key}: {e}")
                    continue
        
        logger.info(f"Bulk download complete: {len(results)}/{total} successful")
        return results
    
    def aggregate_daily(
        self,
        df: pd.DataFrame,
        agg_func: str = 'mean'
    ) -> pd.DataFrame:
        """Agrega datos sub-diarios a resolución diaria.

        Args:
            df: DataFrame con columnas ``tiempo`` y ``valor``.
            agg_func: Función de agregación:
                ``"mean"`` (promedio), ``"sum"`` (suma),
                ``"min"`` (mínimo), ``"max"`` (máximo).

        Returns:
            ``pd.DataFrame`` con datos diarios.

        Example:
            >>> df_diario = downloader.aggregate_daily(df, agg_func="mean")
        """
        if df.empty or 'tiempo' not in df.columns:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        if agg_func == 'mean':
            df_daily = df.resample('D').mean()
        elif agg_func == 'sum':
            df_daily = df.resample('D').sum()
        elif agg_func == 'min':
            df_daily = df.resample('D').min()
        elif agg_func == 'max':
            df_daily = df.resample('D').max()
        else:
            raise ValueError(f"Unknown aggregation function: {agg_func}")
        
        df_daily = df_daily.reset_index()
        return df_daily
    
    def aggregate_temperature_daily(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Agrega temperatura a resolución diaria con min/max/media.

        Args:
            df: DataFrame con columnas ``tiempo`` y ``valor``.

        Returns:
            ``pd.DataFrame`` con columnas: ``tiempo``, ``tmean``, ``tmin``, ``tmax``.

        Example:
            >>> df_temp = downloader.aggregate_temperature_daily(df)
            >>> print(df_temp.columns.tolist())
            ['tiempo', 'tmean', 'tmin', 'tmax']
        """
        if df.empty or 'tiempo' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        df_daily = df.resample('D').agg({
            'valor': ['mean', 'min', 'max']
        })
        
        df_daily.columns = ['tmean', 'tmin', 'tmax']
        df_daily = df_daily.reset_index()
        
        return df_daily
