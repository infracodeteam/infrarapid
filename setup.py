import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="",
    version="0.0.1",
    author="InfraCode",
    author_email="",
    description="InfraRapid package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/infracodeteam/infrarapid",
    project_urls={
        "Bug Tracker": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
