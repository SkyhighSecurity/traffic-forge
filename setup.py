"""Setup script for Shadow IT Log Generator."""

from setuptools import setup, find_packages
import os
import sys

# Add src to path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from shadow_it_generator._version import __version__, __author__, __description__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="skyhigh-traffic-forge",
    version=__version__,
    author=__author__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skyhighsecurity/traffic-forge",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "full": [
            "pydantic>=2.0.0",
            "faker>=20.0.0",
            "numpy>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "skyhigh-traffic-forge=shadow_it_generator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "shadow_it_generator": [
            "config/templates/*",
            "config/templates/cloud-services/*",
        ],
    },
)