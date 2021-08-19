from setuptools import setup, find_packages

setup(
    name="straylib",
    version="0.0.1",
    author="Stray Robots",
    author_email="ken@strayrobots.io",
    description="Stray main utility library",
    url="https://strayrobots.io",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'trimesh',
        'scipy',
        'pillow',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'straylib-scale-calibration=scripts.scale_calibration:main',
            'straylib-dataset-import=scripts.import:main'
        ]
    }
)
