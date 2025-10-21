from setuptools import setup, find_packages

setup(
    name="life",
    version="0.1.0",
    description="Conway's Game of Life implementation with visualizations",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.0",
        "numpy>=1.20",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ],
    },
)