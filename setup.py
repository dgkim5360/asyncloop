import re
from pathlib import Path
from setuptools import setup


with (Path(__file__).parent / 'asyncloop' / '__init__.py').open() as f:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             f.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='asyncloop',
    version=version,
    description=(
        'A Celery-like event loop with asyncio '
        'and no more dependencies'
    ),
    long_description=long_description,
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='asyncio celery event loop',
    url='https://github.com/dgkim5360/asyncloop',
    author='Don Kim',
    author_email='dgkimdev@gmail.com',
    packages=['asyncloop'],
    license='MIT',
    zip_safe=False,
)
