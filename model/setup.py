from setuptools import setup

setup(
    name="straymodel",
    version="0.0.1",
    author="Stray Robots",
    author_email="ken@strayrobots.io",
    description="Stray Robots modeling and learning library.",
    url="https://strayrobots.io",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=['straymodel'],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'stray-model-bake=bake:bake',
        ]
    }
)
