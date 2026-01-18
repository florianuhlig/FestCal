"""Setup configuration for FestCal."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="festcal",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Rhein-Main Event Aggregator with iCalendar/CalDAV export",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/florianuhlig/FestCal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "festcal-web=src.web.app:main",
            "festcal-caldav=src.calendar.caldav_server:main",
            "festcal-export=src.calendar.generator:main",
            "festcal-db=src.database.db_handler:main",
        ],
    },
)
