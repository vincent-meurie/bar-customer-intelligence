from setuptools import setup, find_packages

setup(
    name="bar-customer-intelligence",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        line.strip()
        for line in open("requirements/base.txt")
        if line.strip() and not line.startswith("#") and not line.startswith("-r")
    ],
)