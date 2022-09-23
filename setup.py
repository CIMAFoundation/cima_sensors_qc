import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="risicolive_QC",
    version="0.0.0",
    author="Nicolò Perello",
    author_email="nicolo.perello@cimafoundation.org",
    description="data quality check algorithm for RISICO Live stations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Perello-nico/risicolive_QC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'pandas',
        'typing',
        'json',
      ],
)