from setuptools import setup, find_packages

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
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["click", "tensorboard", "cmake", "fvcore", "torchvision", "torch", "trimesh", "pyrender", "opencv-python"],
    setup_requires=["fvcore", "torch==1.9", "torchvision==0.10"],
    dependency_links=["https://download.pytorch.org/whl/cu111/torch_stable.html", "git+git://github.com/facebookresearch/fvcore.git@2d073f1b713f6ff3bb310af9a4313a5e8e03f49c"],
    entry_points={
        'console_scripts': [
            'stray-model-bake=straymodel.verbs.bake:bake',
            'stray-model-generate=straymodel.verbs.generate:generate',
            'stray-model-evaluate=straymodel.verbs.evaluate:evaluate'
        ]
    }
)
