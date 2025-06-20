from setuptools import setup, find_packages

setup(
    name="crisp_threat_intel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Django>=4.2.10",
        "djangorestframework>=3.14.0",
        "stix2>=3.0.1",
        "taxii2-client>=2.3.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "cryptography>=41.0.5"
    ],
    author="CRISP Development Team",
    description="CRISP Threat Intelligence Package",
)