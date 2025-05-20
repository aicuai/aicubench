
from setuptools import setup, find_packages

setup(
    name="aicubench",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "jinja2",
        "requests",
        "pillow",
        "psutil",
        "platformdirs"
    ],
    entry_points={
        'console_scripts': [
            'aicubench=aicubench.__main__:main',
        ],
    },
    author="AICU Inc.",
    description="Benchmarking toolkit for generative AI platforms",
    license="Apache License 2.0",
    include_package_data=True,
    zip_safe=False
)
