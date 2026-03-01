"""
Data cleaning functions for accelerometer data
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, List


def remove_outliers(
    data: Union[np.ndarray, pd.Series],
    method: str = 'zscore',
    threshold: float = 3.0
) -> Union[np.ndarray, pd.Series]:
    """
    Remove outliers from data.
    
    Parameters
    ----------
    data : array-like
        Input data
    method : str
        Method for outlier detection ('zscore', 'iqr', 'mad')
    threshold : float
        Threshold for outlier detection
    
    Returns
    -------
    array-like
        Data with outliers replaced by NaN
    """
    data = data.copy()
    
    if method == 'zscore':
        mean = np.nanmean(data)
        std = np.nanstd(data)
        z_scores = np.abs((data - mean) / std)
        mask = z_scores > threshold
        
    elif method == 'iqr':
        q1 = np.nanpercentile(data, 25)
        q3 = np.nanpercentile(data, 75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        mask = (data < lower) | (data > upper)
        
    elif method == 'mad':
        median = np.nanmedian(data)
        mad = np.nanmedian(np.abs(data - median))
        modified_z = 0.6745 * (data - median) / mad
        mask = np.abs(modified_z) > threshold
        
    else:
        raise ValueError(f"Unknown method: {method}")
    
    if isinstance(data, pd.Series):
        data[mask] = np.nan
    else:
        data[mask] = np.nan
    
    return data


def fill_missing_values(
    data: Union[np.ndarray, pd.Series, pd.DataFrame],
    method: str = 'interpolate',
    **kwargs
) -> Union[np.ndarray, pd.Series, pd.DataFrame]:
    """
    Fill missing values in data.
    
    Parameters
    ----------
    data : array-like
        Input data with missing values
    method : str
        Method for filling ('interpolate', 'mean', 'median', 'ffill', 'bfill')
    **kwargs : dict
        Additional arguments for interpolation
    
    Returns
    -------
    array-like
        Data with filled values
    """
    data = data.copy()
    
    if isinstance(data, np.ndarray):
        data = pd.Series(data)
        is_array = True
    else:
        is_array = False
    
    if method == 'interpolate':
        data = data.interpolate(method='linear', **kwargs)
    elif method == 'mean':
        data = data.fillna(data.mean())
    elif method == 'median':
        data = data.fillna(data.median())
    elif method == 'ffill':
        data = data.ffill()
    elif method == 'bfill':
        data = data.bfill()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    if is_array:
        return data.values
    return data


def remove_offset(
    data: Union[np.ndarray, pd.Series],
    method: str = 'mean'
) -> Union[np.ndarray, pd.Series]:
    """
    Remove DC offset from signal.
    
    Parameters
    ----------
    data : array-like
        Input signal
    method : str
        Method for offset removal ('mean', 'median', 'first_n')
    
    Returns
    -------
    array-like
        Signal with offset removed
    """
    if method == 'mean':
        offset = np.nanmean(data)
    elif method == 'median':
        offset = np.nanmedian(data)
    elif method == 'first_n':
        offset = np.nanmean(data[:100])
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return data - offset
