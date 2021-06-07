import setuptools

import pydbhub

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pydbhub',
    version=pydbhub.__version__,
    author="LeMoussel",
    author_email="cnhx27@gmail.com",
    license='MIT',
    url="https://github.com/LeMoussel/pydbhub",
    description='A Python library for accessing and using SQLite databases on DBHub.io',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "pydbhub"},
    packages=setuptools.find_packages(where="pydbhub"),
    install_requires=[
        'requests',
        'python_dateutil',
        'rich'
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

# Packaging Python Projects: https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi
#
#   python setup.py test
#   python setup.py bdist_wheel
#
#   twine check dist/<paquet .whl> or dist/*
#   twine upload dist/<paquet .whl> or dist/*
