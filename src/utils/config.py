"""
Configuration utilities
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str = "configs/project.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str
        Path to configuration file
    
    Returns
    -------
    dict
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def load_sensor_config(
    sensor_name: str,
    config_path: str = "configs/project.yaml"
) -> Dict[str, Any]:
    """
    Load sensor-specific configuration.
    
    Parameters
    ----------
    sensor_name : str
        Name of the sensor ('sensor_a' or 'sensor_b')
    config_path : str
        Path to sensors configuration file
    
    Returns
    -------
    dict
        Sensor configuration dictionary
    """
    config = load_config(config_path)
    
    sensors = config.get("sensors", config)
    if sensor_name not in sensors:
        raise ValueError(f"Sensor '{sensor_name}' not found in config")
    
    return sensors[sensor_name]


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns
    -------
    Path
        Project root path
    """
    current = Path(__file__).resolve()
    
    for parent in current.parents:
        if (parent / 'configs').exists():
            return parent
    
    return Path.cwd()
