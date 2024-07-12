import json
import os
import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

with open(os.path.join(os.path.dirname(__file__), "src", "minceraft", "config.json"), "r", encoding="utf-8") as f:
    version = json.load(f)[0]["launcher_version"]


setup(
    name="minceraft",
    version=version,
    description="A fast minecraft launcher",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CdrJohannsen/minceraft",
    author="Cdr_Johannsen",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment",
    ],
    keywords="Minceraft, Python, Quick, Fast, Minecraft",
    python_requires=">=3.7, <4",
    install_requires=["msmcauth", "minecraft-launcher-lib", "argparse"],
    extras_require={"gtk": "pygobject"},
    packages=["minceraft"],
    package_dir={"": "src"},
    package_data={
        "minceraft": ["azure.json", "config.json", "logo.txt", "minceraft.png", "minceraft_gtk.ui"],
    },
    data_files=[
        ("share/applications", ["minceraft.desktop"]),
        ("share/icons/hicolor/256x256/apps", ["src/minceraft/minceraft.png"]),
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "minceraft=minceraft.minceraft_main:main",
        ]
    },
)
