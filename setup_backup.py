from setuptools import setup, find_packages

setup(
    name="ckart-cli",
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
            "ckart=ckart.main:main"
        ]
    },
	author="Project ckart",
    description="ckart CLI tool to manage VMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
