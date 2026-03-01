"""
Input/Output utilities for sensor data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Dict, Optional
import yaml


def load_sensor_data(
    filepath: Union[str, Path],
    sensor_config: Optional[Dict] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Load sensor data from file.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the data file
    sensor_config : dict, optional
        Sensor configuration from configs/project.yaml
    **kwargs : dict
        Additional arguments passed to pd.read_csv
    
    Returns
    -------
    pd.DataFrame
        Loaded sensor data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if sensor_config:
        data_format = sensor_config.get('data_format', {})
        delimiter = data_format.get('delimiter', ',')
        header_rows = data_format.get('header_rows', 0)
        
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            header=header_rows - 1 if header_rows > 0 else None,
            **kwargs
        )
    else:
        df = pd.read_csv(filepath, **kwargs)
    
    return df


def save_results(
    data: Union[pd.DataFrame, Dict],
    filepath: Union[str, Path],
    format: str = 'csv'
) -> None:
    """
    Save analysis results to file.
    
    Parameters
    ----------
    data : pd.DataFrame or dict
        Data to save
    filepath : str or Path
        Output file path
    format : str
        Output format ('csv', 'xlsx', 'json')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, dict):
        data = pd.DataFrame(data)
    
    if format == 'csv':
        data.to_csv(filepath, index=False)
    elif format == 'xlsx':
        data.to_excel(filepath, index=False)
    elif format == 'json':
        data.to_json(filepath, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_multiple_files(
    directory: Union[str, Path],
    pattern: str = "*.csv",
    sensor_config: Optional[Dict] = None
) -> Dict[str, pd.DataFrame]:
    """
    Load multiple data files from a directory.
    
    Parameters
    ----------
    directory : str or Path
        Directory containing data files
    pattern : str
        Glob pattern for file matching
    sensor_config : dict, optional
        Sensor configuration
    
    Returns
    -------
    dict
        Dictionary mapping filenames to DataFrames
    """
    directory = Path(directory)
    files = sorted(directory.glob(pattern))
    
    data = {}
    for f in files:
        data[f.stem] = load_sensor_data(f, sensor_config)
    
    return data
