"""This module handles the base functionality."""


class HandlerBase:
    """
    Base class for all feature‐handlers. Delegates unknown attributes
    (methods & properties) up to the main App instance.
    """
    def __init__(self, parent):
        self._parent = parent

    def __getattr__(self, name):
        return getattr(self._parent, name)
