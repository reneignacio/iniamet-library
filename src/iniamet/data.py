"""
Data downloading module.

Handles time series data retrieval with caching and aggregation support.
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
    """Handles data downloads from INIA API."""
    
    def __init__(self, api: APIClient, cache: Optional[CacheManager] = None):
        """
        Initialize data downloader.
        
        Args:
            api: API client instance
            cache: Optional cache manager
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
        """
        Download time series data with optional aggregation.
        
        Args:
            station: Station code (e.g., "INIA-47")
            variable: Variable ID (e.g., 2002 for temperature) or name
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            use_cache: Use cached data if available (default: True)
            aggregation: Optional temporal aggregation:
                - None or 'raw': Return raw data (default)
                - 'D' or 'daily': Daily aggregation
                - 'W': Weekly aggregation
                - 'M': Monthly aggregation
                - 'H': Hourly aggregation
                - Any pandas resample rule
            
        Returns:
            DataFrame with columns: tiempo (datetime), valor (float)
            If aggregation is applied, may include additional columns
            depending on variable type (e.g., valor_min, valor_max for temperature)
            
        Raises:
            ValueError: If dates are invalid or variable ID is unknown
            
        Example:
            >>> from iniamet.data import DataDownloader
            >>> from iniamet.utils import VAR_TEMPERATURA_MEDIA
            >>> downloader = DataDownloader(api_client)
            >>> 
            >>> # Raw data (15-minute intervals)
            >>> df = downloader.get_data('INIA-47', VAR_TEMPERATURA_MEDIA,
            ...                          '2024-09-01', '2024-09-30')
            >>> 
            >>> # Daily aggregation
            >>> df_daily = downloader.get_data('INIA-47', VAR_TEMPERATURA_MEDIA,
            ...                                 '2024-09-01', '2024-09-30',
            ...                                 aggregation='D')
        """
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
        """
        Apply temporal aggregation to time series data.
        
        Args:
            df: Raw data DataFrame with 'tiempo' and 'valor' columns
            variable_id: Variable ID to determine aggregation method
            rule: Pandas resample rule (e.g., 'D', 'W', 'M')
            
        Returns:
            Aggregated DataFrame
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
        """
        Download data for multiple stations and variables.
        
        Args:
            stations: List of station codes
            variables: List of variable IDs
            start_date: Start date
            end_date: End date
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping "station_variable" to DataFrames
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
        """
        Aggregate sub-daily data to daily.
        
        Args:
            df: DataFrame with 'tiempo' and 'valor' columns
            agg_func: Aggregation function ('mean', 'sum', 'min', 'max')
            
        Returns:
            Daily aggregated DataFrame
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
        """
        Aggregate temperature data to daily min/max/mean.
        
        Args:
            df: DataFrame with 'tiempo' and 'valor' columns
            
        Returns:
            Daily DataFrame with columns: tiempo, tmean, tmin, tmax
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
