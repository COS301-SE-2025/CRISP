"""
Setup script for CRISP Anonymization System
"""

from setuptools import setup, find_packages
import os

# Read README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "crisp_anonymization", "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read version from __init__.py
version = {}
with open(os.path.join(current_dir, "crisp_anonymization", "__init__.py")) as f:
    exec(f.read(), version)

setup(
    name="crisp-anonymization",
    version=version.get("__version__", "1.0.0"),
    author="CRISP Development Team",
    author_email="dev@crisp-system.org",
    description="Flexible anonymization system for threat intelligence sharing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crisp-system/anonymization",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses Python standard library only
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "enhanced": [
            "requests>=2.28.0",
            "cryptography>=38.0.0",
            "pyyaml>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crisp-anonymize=crisp_anonymization.demo:demonstrate_anonymization",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/crisp-system/anonymization/issues",
        "Source": "https://github.com/crisp-system/anonymization",
        "Documentation": "https://crisp-anonymization.readthedocs.io/",
    },
    keywords="anonymization, threat-intelligence, cybersecurity, privacy, crisp",
    package_data={
        "crisp_anonymization": ["README.md"],
    },
    zip_safe=False,
)