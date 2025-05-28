"""Setup script for Shadow IT Log Generator."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="skyhigh-traffic-forge",
    version="1.0.0",
    author="Skyhigh Security Team",
    description="Generate realistic web gateway traffic logs for CASB testing and demonstrations",
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