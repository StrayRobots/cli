from setuptools import setup, find_packages

setup(
    name="straylabel",
    version="0.0.1",
    author="Stray Robots",
    author_email="ken@strayrobots.io",
    description="Stray utility scripts for working with labels.",
    url="https://strayrobots.io",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'stray-label-generate=straylabel.verbs.generate:generate',
            'stray-label-show=straylabel.verbs.show:show'
        ]
    }
)
