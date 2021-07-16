from setuptools import setup

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
    packages=['straylib', 'model', 'label'],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'straylib-label-segment=label.scripts.segmentation:main',
            'straylib-label-generate=label.scripts.generate:main',
            'straylib-label-preview=label.scripts.preview:main',
            'straylib-model-bake=model.scripts.bake:bake',
        ]
    }
)
