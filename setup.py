from setuptools import setup, find_packages

import pygot


with open('README.md') as f:
    readme = f.read()

setup(
    name=pygot.__name__,
    version=pygot.__version__,
    packages=find_packages(),
    author=f'{pygot.__author__} <{pygot.__author_email__}>',
    license=pygot.__license__,
    description=pygot.__doc__.splitlines()[0],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=pygot.__url__,
    classifiers=[
        'Topic :: Games/Entertainment :: Board Games',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Typing :: Typed',
    ],
)
