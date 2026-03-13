"""Tests for frame capture module."""

import sys
import inspect
from devliverepl.capture import capture_call_site, get_current_context, ContextRegistry


def test_capture_call_site_captures_locals():
    """Should capture local variables from calling frame."""
    local_var = "test_value"
    another_local = 42

    captured = capture_call_site()

    assert "local_var" in captured.locals
    assert captured.locals["local_var"] == "test_value"
    assert "another_local" in captured.locals
    assert captured.locals["another_local"] == 42


def test_capture_call_site_captures_globals():
    """Should capture global variables from calling frame."""
    captured = capture_call_site()

    # Should have globals like __name__, __file__, etc.
    assert "__name__" in captured.globals


def test_capture_call_site_captures_frame_info():
    """Should capture frame information."""
    captured = capture_call_site()

    assert captured.filename is not None
    assert captured.lineno is not None
    assert captured.function is not None
    assert "test_capture_call_site_captures_frame_info" in captured.function


def test_context_registry_store_and_retrieve():
    """ContextRegistry should store and retrieve contexts."""
    registry = ContextRegistry()
    context = capture_call_site()

    registry.store("test", context)

    retrieved = registry.get("test")
    assert retrieved is context


def test_context_registry_get_latest():
    """get_latest() should return most recently stored context."""
    registry = ContextRegistry()

    context1 = capture_call_site()
    registry.store("first", context1)

    context2 = capture_call_site()
    registry.store("second", context2)

    latest = registry.get_latest()
    assert latest is context2


def test_context_registry_list_names():
    """list_names() should return all stored context names."""
    registry = ContextRegistry()

    registry.store("ctx1", capture_call_site())
    registry.store("ctx2", capture_call_site())

    names = registry.list_names()
    assert "ctx1" in names
    assert "ctx2" in names


def test_context_registry_clear():
    """clear() should remove all stored contexts."""
    registry = ContextRegistry()
    registry.store("test", capture_call_site())

    registry.clear()

    assert registry.list_names() == []
    assert registry.get_latest() is None


def test_capture_context_has_to_dict():
    """CapturedContext should have to_dict() for merging into REPL namespace."""
    captured = capture_call_site()
    merged = captured.to_dict()

    # Should include locals and globals
    assert isinstance(merged, dict)
    # Should have captured function from test
    assert "capture_call_site" in merged or any(v for k, v in merged.items() if "capture" in k.lower())
