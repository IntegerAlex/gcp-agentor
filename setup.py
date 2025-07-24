from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gcp-agentor",
    version="0.1.0",
    author="GCP Agentor Team",
    description="GCP-Based Multi-Agent Orchestration Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/gcp-agentor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "google-cloud-firestore>=2.0.0",
        "google-cloud-aiplatform>=1.35.0",
        "google-cloud-pubsub>=2.0.0",
        "google-auth>=2.0.0",
        "dataclasses-json>=0.6.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gcp-agentor=gcp_agentor.cli:main",
        ],
    },
) 