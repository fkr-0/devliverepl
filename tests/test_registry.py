"""Tests for object registry module."""

import pytest
from devliverepl.registry import ObjectRegistry, register, expose, get_exposed_objects, get_global_registry


class TestClass:
    """Test class for registration."""
    pass


def test_object_registry_register_by_name():
    """Should register object with explicit name."""
    registry = ObjectRegistry()
    obj = TestClass()

    registry.register(obj, name="test_obj")

    retrieved = registry.get("test_obj")
    assert retrieved is obj


def test_object_registry_register_auto_name():
    """Should register object with automatic name."""
    registry = ObjectRegistry()

    my_var = TestClass()
    registry.register(my_var)

    # Should use variable name or class name
    names = registry.list_names()
    assert len(names) > 0
    assert registry.get(names[0]) is my_var


def test_object_registry_register_replace():
    """Registering with same name should replace existing."""
    registry = ObjectRegistry()

    obj1 = TestClass()
    obj2 = TestClass()

    registry.register(obj1, name="shared")
    registry.register(obj2, name="shared")

    assert registry.get("shared") is obj2


def test_object_registry_get_nonexistent():
    """Getting nonexistent name should return None."""
    registry = ObjectRegistry()

    assert registry.get("nonexistent") is None


def test_object_registry_list_names():
    """list_names() should return all registered names."""
    registry = ObjectRegistry()

    registry.register(TestClass(), name="first")
    registry.register(TestClass(), name="second")

    names = registry.list_names()
    assert "first" in names
    assert "second" in names


def test_object_registry_clear():
    """clear() should remove all registered objects."""
    registry = ObjectRegistry()
    registry.register(TestClass(), name="test")

    registry.clear()

    assert registry.list_names() == []
    assert registry.get("test") is None


def test_expose_decorator():
    """@expose decorator should register decorated class."""
    registry = ObjectRegistry()

    @expose(registry=registry)
    class MyService:
        pass

    names = registry.list_names()
    assert "MyService" in names
    assert isinstance(registry.get("MyService"), type)  # Class object


def test_expose_decorator_with_name():
    """@expose decorator should respect custom name."""
    registry = ObjectRegistry()

    @expose(name="custom", registry=registry)
    class MyService:
        pass

    assert "custom" in registry.list_names()
    assert registry.get("custom") is MyService


def test_expose_decorator_function():
    """@expose should work on functions too."""
    registry = ObjectRegistry()

    @expose(registry=registry)
    def my_function():
        return 42

    assert "my_function" in registry.list_names()


def test_global_registry_singleton():
    """Global registry functions should use shared instance."""
    obj = TestClass()
    register(obj, name="global_test")

    assert get_global_registry().get("global_test") is obj


def test_get_exposed_objects():
    """get_exposed_objects() should return all registered objects."""
    obj1 = TestClass()
    obj2 = TestClass()

    register(obj1, name="obj1")
    register(obj2, name="obj2")

    exposed = get_exposed_objects()
    assert "obj1" in exposed
    assert "obj2" in exposed
    assert exposed["obj1"] is obj1
    assert exposed["obj2"] is obj2
