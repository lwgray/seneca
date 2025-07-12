"""
Setup script for Seneca - Marcus Visualization Platform
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="seneca-viz",
    version="1.0.0",
    description="Open-source conversation visualization for Marcus AI systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marcus AI Team",
    author_email="team@marcus-ai.dev",
    url="https://github.com/marcus-ai/seneca",
    project_urls={
        "Documentation": "https://seneca.marcus-ai.dev",
        "Bug Tracker": "https://github.com/marcus-ai/seneca/issues",
        "Source Code": "https://github.com/marcus-ai/seneca",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json"],
        "processors": ["templates/*.html", "static/**/*"],
        "api": ["templates/*.html", "static/**/*"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
        "all": [
            # Combination of dev and docs
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
            "bandit>=1.7.0",
            "safety>=2.3.0",
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "seneca=seneca_cli:main",
            "seneca-server=seneca_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    keywords="marcus agent orchestration visualization analytics dashboard monitoring",
    zip_safe=False,
)