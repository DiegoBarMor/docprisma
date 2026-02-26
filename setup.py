from setuptools import setup, find_packages

setup(
    name="docprisma",
    version="1.0.0",
    description="Tool for fast inspection and comparison of JSON files inside the terminal",
    keywords="json terminal tui",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DiegoBarMor",
    author_email="diegobarmor42@gmail.com",
    url="https://github.com/diegobarmor/docprisma",
    license="MIT",
    packages=find_packages(),
    install_requires=["prismatui==0.3.2"],
    entry_points={
        "console_scripts": [
            "docprisma=docprisma.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
