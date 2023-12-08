"""Client library for the Ansys file transfer tool."""

import importlib.metadata

from ._client import Client

__all__ = ["Client"]

__version__ = importlib.metadata.version(__name__.replace(".", "-"))
