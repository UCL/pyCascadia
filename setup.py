from setuptools import setup

with open('README.md', 'r', newline='', encoding='utf-8') as readme_file:
    long_description = readme_file.read()
    long_description_content_type = 'text/markdown'

setup(
    long_description = long_description,
    long_description_content_type = long_description_content_type,
    version = "1.0.3",
)
