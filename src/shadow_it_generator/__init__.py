"""
Shadow IT Log Generator

A comprehensive tool for generating realistic shadow IT network traffic logs
for security testing, training, and simulation purposes.
"""

from ._version import __version__, __version_info__, __release_date__, __author__, __description__
from .main import main

__all__ = ["main", "__version__", "__version_info__", "__release_date__", "__author__", "__description__"]