import setuptools

setuptools.setup(
    name="",
    version="0.0.1",
    author="InfraCode",
    author_email="",
    description="InfraRapid package",
    long_description="""Infrarapid tools allows you to create,
                        configure and deploy same infrastructure
                        over multiple cloud providers""",
    long_description_content_type="text/markdown",
    url="https://github.com/infracodeteam/infrarapid",
    project_urls={
        "Bug Tracker": "https://github.com/infracodeteam/infrarapid/issues/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
