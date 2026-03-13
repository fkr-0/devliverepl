"""Tests for configuration module."""

import pytest
from dataclasses import is_dataclass


def test_config_is_dataclass():
    """ReplConfig should be a dataclass."""
    from devliverepl.config import ReplConfig
    assert is_dataclass(ReplConfig)


def test_default_config_values():
    """ReplConfig should have correct default values."""
    from devliverepl.config import ReplConfig

    config = ReplConfig()
    assert config.port == 8022
    assert config.host == "127.0.0.1"
    assert config.banner_level == "rich"
    assert config.banner_func is None
    assert config.auto_import_exposed is True
    assert config.log_connections is True
    assert config.log_commands is False
    assert config.shutdown_timeout == 30.0
    assert config.enable_atexit is True
    assert config.discover_local_modules is True


def test_configure_updates_values():
    """configure() should update config values."""
    from devliverepl.config import configure, get_config

    configure(port=9999, banner_level="minimal")
    config = get_config()
    assert config.port == 9999
    assert config.banner_level == "minimal"


def test_configure_rejects_unknown_options():
    """configure() should raise ValueError for unknown options."""
    from devliverepl.config import configure

    with pytest.raises(ValueError, match="Unknown config option"):
        configure(unknown_option=True)


def test_configure_updates_multiple_values():
    """configure() should update multiple values at once."""
    from devliverepl.config import configure, get_config

    configure(
        port=8023,
        host="0.0.0.0",
        banner_level="minimal",
        log_commands=True
    )
    config = get_config()
    assert config.port == 8023
    assert config.host == "0.0.0.0"
    assert config.banner_level == "minimal"
    assert config.log_commands is True


def test_module_ignore_patterns_default():
    """Default ignore patterns should exclude common patterns."""
    from devliverepl.config import ReplConfig

    config = ReplConfig()
    assert "test_" in config.module_ignore_patterns
    assert "tests." in config.module_ignore_patterns
    assert "__pycache__" in config.module_ignore_patterns
