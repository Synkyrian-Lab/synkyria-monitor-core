from setuptools import setup, find_packages

setup(
    name="synkyria", 
    version="1.0.1",
    description="Synkyria Monitor – Core finite-horizon stability companion for training runs.",
    author="Panagiotis Kalomoirakis",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.23",
    ],
)
