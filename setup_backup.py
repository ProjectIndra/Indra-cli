from setuptools import setup, find_packages

setup(
    name="indra-cli",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
		"argparse",
		"tabulate",
		"pynacl",
		"psutil"
    ],
    entry_points={
        "console_scripts": [
            "indra=indra.main:main"
        ]
    },
	author="Project Indra",
    description="Indra CLI tool to manage VMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
