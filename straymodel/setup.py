from setuptools import setup, find_packages

setup(
    name="straymodel",
    version="0.0.2",
    author="Stray Robots",
    author_email="ken@strayrobots.io",
    description="Stray Robots modeling and learning library.",
    url="https://strayrobots.io",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["click", "tensorboard", "cmake", "fvcore", "torchvision", "torch", "trimesh", "pyrender", "opencv-python", "omegaconf", "scikit-spatial"],
    entry_points={
        'console_scripts': [
            'stray-model-bake=straymodel.verbs.bake:bake',
            'stray-model-generate=straymodel.verbs.generate:generate',
            'stray-model-evaluate=straymodel.verbs.evaluate:evaluate'
        ]
    }
)
