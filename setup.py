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

def requires_from_file(filename):
    return open(filename).read().splitlines()

LONG_DESCRIPTION = (this_directory / "README.md").read_text()
SHORT_DESCRIPTION = "Utility for web scraping."

setup(
    name="scrapinghelper",
    version=get_version('scrapinghelper/versions.py'),
    license="MIT",
    install_requires=requires_from_file('requirements.txt'),
    extras_require={
        "socks": ["PySocks>=1.5.6, !=1.5.7"],
        "converter": [ "multimethod>=1.8" ],
    },
    author="Goichi (Iisaka) Yukawa",
    author_email="iisaka51@gmail.com",
    url="https://github.com/iisaka51/scrapinghelper",
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'': [ 'data/*.csv', 'data/LICENSE' ]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
