# setup.py
from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setup(
    name="testpilotai",
    version="0.1",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    py_modules=["main"],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "testpilotai = main:main",
        ],
    },
)
