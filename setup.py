from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def get_version(rel_path):
    for line in (this_directory / rel_path).read_text().splitlines():
        if line.startswith('__VERSION__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

LONG_DESCRIPTION = (this_directory / "README.md").read_text()
SHORT_DESCRIPTION = "Utility for web scraping."

requirements = [
    "request_html",
    "validators",
    "types-requests",
]

setup(
    name="scrapper-tools",
    version=get_version('scrapper-tools/versions.py'),
    license="MIT",
    install_requirements=requirements,
    author="Goichi (Iisaka) Yukawa",
    author_email="iisaka51@gmail.com",
    url="https://github.com/iisaka51/scrapper-tools",
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
