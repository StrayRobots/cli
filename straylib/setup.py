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
        'numpy',
        'scikit-video',
        'pycocotools'
    ],
    entry_points={
        'console_scripts': [
            'straylib-scale-calibration=scripts.scale_calibration:main',
            'straylib-dataset-import=scripts.dataset_import:main',
            'straylib-dataset-cut=scripts.cut:main',
            'straylib-dataset-bake=scripts.bake:main',
            'straylib-dataset-show=scripts.show:main'
        ]
    }
)
