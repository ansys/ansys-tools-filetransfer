"""
utilities.

filetransfer
"""

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from ._client import Client

__all__ = ["Client"]

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
