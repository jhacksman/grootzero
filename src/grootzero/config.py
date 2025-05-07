"""
Configuration management for the GROOTZERO project.

This module provides utilities for loading, saving, and validating configuration
for the various components of the GROOTZERO system.
"""

import os
import yaml
from typing import Dict, Any, Optional


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/default_config.yaml")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file. If None, the default configuration is loaded.
        
    Returns:
        Dictionary containing the configuration.
        
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the configuration file is not valid YAML.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
        
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing configuration file: {e}")


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a YAML file.
    
    Args:
        config: Dictionary containing the configuration.
        config_path: Path to save the configuration file.
        
    Raises:
        yaml.YAMLError: If the configuration cannot be serialized to YAML.
    """
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        try:
            yaml.dump(config, f, default_flow_style=False)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error serializing configuration: {e}")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and values.
    
    Args:
        config: Dictionary containing the configuration.
        
    Returns:
        True if the configuration is valid, False otherwise.
    """
    required_sections = ["simulation", "learning", "groot_n1"]
    for section in required_sections:
        if section not in config:
            print(f"Missing required configuration section: {section}")
            return False
    
    if "simulation" in config:
        sim_config = config["simulation"]
        if not isinstance(sim_config, dict):
            print("Simulation configuration must be a dictionary")
            return False
            
        required_sim_params = ["environment_path", "physics_dt"]
        for param in required_sim_params:
            if param not in sim_config:
                print(f"Missing required simulation parameter: {param}")
                return False
    
    if "learning" in config:
        learning_config = config["learning"]
        if not isinstance(learning_config, dict):
            print("Learning configuration must be a dictionary")
            return False
            
        required_learning_params = ["reward_type", "history_size"]
        for param in required_learning_params:
            if param not in learning_config:
                print(f"Missing required learning parameter: {param}")
                return False
    
    if "groot_n1" in config:
        groot_config = config["groot_n1"]
        if not isinstance(groot_config, dict):
            print("GR00T N1 configuration must be a dictionary")
            return False
            
        required_groot_params = ["api_type", "mock_enabled"]
        for param in required_groot_params:
            if param not in groot_config:
                print(f"Missing required GR00T N1 parameter: {param}")
                return False
    
    return True


def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration for the GROOTZERO system.
    
    Returns:
        Dictionary containing the default configuration.
    """
    return {
        "simulation": {
            "environment_path": "default_environment",
            "physics_dt": 0.01,
            "render_enabled": True,
            "max_steps": 1000,
            "domain_randomization": {
                "enabled": True,
                "gravity_range": [-10.0, -9.8],
                "friction_range": [0.5, 1.0],
                "mass_range_factor": [0.8, 1.2]
            }
        },
        "learning": {
            "reward_type": "binary",
            "history_size": 100,
            "selection_strategy": "performance_weighted",
            "learning_rate": 0.001
        },
        "groot_n1": {
            "api_type": "mock",
            "mock_enabled": True,
            "temperature": 0.7,
            "max_tokens": 2048,
            "task_generation": {
                "prompt_template": "default_task_prompt",
                "validation_enabled": True
            },
            "controller_generation": {
                "prompt_template": "default_controller_prompt",
                "validation_enabled": True
            }
        }
    }
