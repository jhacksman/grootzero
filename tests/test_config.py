"""
Tests for the configuration management system.
"""

import os
import pytest
import yaml
from grootzero.config import (
    load_config,
    save_config,
    validate_config,
    get_default_config
)


def test_load_config_default():
    """Test loading the default configuration."""
    config = load_config()
    assert isinstance(config, dict)
    assert "simulation" in config
    assert "learning" in config
    assert "groot_n1" in config


def test_load_config_nonexistent():
    """Test loading a nonexistent configuration file."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/to/config.yaml")


def test_save_and_load_config(tmp_path):
    """Test saving and loading a configuration file."""
    config_path = os.path.join(tmp_path, "test_config.yaml")
    test_config = {
        "test_section": {
            "test_param": "test_value"
        }
    }
    
    save_config(test_config, config_path)
    assert os.path.exists(config_path)
    
    loaded_config = load_config(config_path)
    assert loaded_config == test_config


def test_validate_config_valid():
    """Test validating a valid configuration."""
    valid_config = get_default_config()
    assert validate_config(valid_config) is True


def test_validate_config_invalid_missing_section():
    """Test validating a configuration with a missing section."""
    invalid_config = get_default_config()
    del invalid_config["simulation"]
    assert validate_config(invalid_config) is False


def test_validate_config_invalid_missing_param():
    """Test validating a configuration with a missing parameter."""
    invalid_config = get_default_config()
    del invalid_config["simulation"]["physics_dt"]
    assert validate_config(invalid_config) is False


def test_get_default_config():
    """Test getting the default configuration."""
    default_config = get_default_config()
    assert isinstance(default_config, dict)
    assert "simulation" in default_config
    assert "learning" in default_config
    assert "groot_n1" in default_config
