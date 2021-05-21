"""Backport of python 3.8 functools.cached_property.

cached_property() - computed once per instance, cached as attribute
"""

__all__ = ("cached_property",)

# Standard Library
from sys import version_info

if version_info < (3, 6):
    from cached_property import cached_property
elif version_info >= (3, 8):
    # Standard Library
    from functools import cached_property  # pylint: disable=no-name-in-module
else:
    # Standard Library
    from threading import RLock

    _NOT_FOUND = object()

    # noinspection PyPep8Naming
    class cached_property:  # NOSONAR  # pylint: disable=invalid-name  # noqa: N801
        """Cached property implementation.

        Transform a method of a class into a property whose value is computed once
        and then cached as a normal attribute for the life of the instance.
        Similar to property(), with the addition of caching.
        Useful for expensive computed properties of instances
        that are otherwise effectively immutable.
        """

        def __init__(self, func):
            """Cached property implementation."""
            self.func = func
            self.attrname = None
            self.__doc__ = func.__doc__
            self.lock = RLock()

        def __set_name__(self, owner, name: str):
            """Assign attribute name and owner."""
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    "({} and {}).".format(self.attrname, name)
                )

        def __get__(self, instance, owner=None):
            """Property-like getter implementation.

            :return: property instance if requested on class or value/cached value if requested on instance.
            :raises TypeError: call without calling __set_name__ or no '__dict__' attribute
            """
            if instance is None:
                return self
            if self.attrname is None:
                raise TypeError("Cannot use cached_property instance without calling __set_name__ on it.")
            try:
                cache = instance.__dict__
            except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
                msg = (
                    "No '__dict__' attribute on {} "
                    "instance to cache {} property.".format(type(instance).__name__, self.attrname)
                )
                raise TypeError(msg) from None
            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND:
                with self.lock:
                    # check if another thread filled cache while we awaited lock
                    val = cache.get(self.attrname, _NOT_FOUND)
                    if val is _NOT_FOUND:
                        val = self.func(instance)
                        try:
                            cache[self.attrname] = val
                        except TypeError:
                            msg = (
                                "The '__dict__' attribute on {} instance "
                                "does not support item assignment for caching {} property.".format(type(instance).__name__, self.attrname)
                            )
                            raise TypeError(msg) from None
            return val
