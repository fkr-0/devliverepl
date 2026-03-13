"""Object registry for explicitly exposed objects."""

import threading
from typing import Any, Callable, TypeVar, Optional

T = TypeVar("T")


class ObjectRegistry:
    """Thread-safe registry for explicitly exposed objects."""

    def __init__(self) -> None:
        self._objects: dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(self, obj: Any, name: Optional[str] = None) -> str:
        """Register an object with an optional explicit name.

        Args:
            obj: The object to register.
            name: Explicit name to use. If None, uses object's __name__ or
                  generates a unique name.

        Returns:
            The name used for registration.
        """
        if name is None:
            # Try to get __name__ attribute
            name = getattr(obj, "__name__", None)
            if name is None:
                # Generate unique name
                name = f"obj_{id(obj)}"

        with self._lock:
            self._objects[name] = obj

        return name

    def get(self, name: str) -> Any | None:
        """Get a registered object by name.

        Args:
            name: The name of the object to retrieve.

        Returns:
            The registered object, or None if not found.
        """
        with self._lock:
            return self._objects.get(name)

    def list_names(self) -> list[str]:
        """List all registered object names.

        Returns:
            List of registered names.
        """
        with self._lock:
            return list(self._objects.keys())

    def clear(self) -> None:
        """Remove all registered objects."""
        with self._lock:
            self._objects.clear()

    def to_dict(self) -> dict[str, Any]:
        """Export all registered objects as a dict.

        Returns:
            Dictionary mapping names to objects.
        """
        with self._lock:
            return dict(self._objects)


# Global registry instance
_global_registry = ObjectRegistry()


def register(obj: Any, name: Optional[str] = None) -> str:
    """Register an object in the global registry.

    Args:
        obj: The object to register.
        name: Optional explicit name.

    Returns:
        The name used for registration.
    """
    return _global_registry.register(obj, name=name)


def expose(
    name: Optional[str] = None,
    registry: Optional[ObjectRegistry] = None,
) -> Callable[[T], T]:
    """Decorator to register a class or function in the object registry.

    Args:
        name: Optional name override. Defaults to the class/function name.
        registry: Registry to use. Defaults to global registry.

    Returns:
        Decorator function.

    Example:
        @expose
        class MyService:
            pass

        @expose(name="helper")
        def helper_function():
            pass
    """
    reg = registry if registry is not None else _global_registry

    def decorator(obj: T) -> T:
        reg_name = name if name is not None else getattr(obj, "__name__", None)
        if reg_name is not None:
            reg.register(obj, name=reg_name)
        return obj

    return decorator


def get_exposed_objects() -> dict[str, Any]:
    """Get all globally registered exposed objects.

    Returns:
        Dictionary mapping names to objects.
    """
    return _global_registry.to_dict()


def get_global_registry() -> ObjectRegistry:
    """Get the global object registry.

    Returns:
        The global ObjectRegistry instance.
    """
    return _global_registry
