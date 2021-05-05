from setuptools import setup

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setup(
    install_requires=requirements
)
