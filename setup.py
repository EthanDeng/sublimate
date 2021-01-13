import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sublimate",
    version="0.0.1",
    author="Dongsheng Deng",
    author_email="ddswhu@outlook.com",
    description="sublimate package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EthanDeng/sublimate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)