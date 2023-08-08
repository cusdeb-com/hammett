"""The script for building the Hammett package."""

from pathlib import Path

import pypandoc
from setuptools import find_packages, setup

with Path('requirements.txt').open(encoding='utf-8') as outfile:
    requirements = outfile.read().splitlines()

setup(
    name='hammett',
    version='0.0.1',
    description='The framework for rapid development of Telegram bots '
                'with a clean and pragmatic design.',
    long_description=pypandoc.convert('README.md', 'rst'),
    url='https://github.com/cusdeb-com/hammett',
    author='Evgeny Golyshev',
    author_email='eugulixes@gmail.com',
    maintainer='Evgeny Golyshev',
    maintainer_email='eugulixes@gmail.com',
    license='Apache License, Version 2.0',
    packages=find_packages(exclude=('demos.*', 'demos', 'tests.*', 'tests')),
    include_package_data=True,
    data_files=[('', ['requirements.txt'])],
    install_requires=requirements,
    python_requires='>=3.10',
    keywords='python telegram bot api',
    project_urls={
        'Code': 'https://github.com/cusdeb-com/hammett',
        'Tracker': 'https://github.com/cusdeb-com/hammett/issues',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Hammett',
        'License :: OSI Approved :: Apache License, Version 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
    ],
)
