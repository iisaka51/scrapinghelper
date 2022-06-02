from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="web_scrapper",
    version="0.1.0",
    license="MIT",
    install_requirements=[
        "request_html",
        "types-requests",
        ],
    author="Goichi (Iisaka) Yukawa",
    author_email="iisaka51@gmail.com",
    url="https://github.com/iisaka51/web_scrapper",
    description="Helper class for web scrapinf.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
