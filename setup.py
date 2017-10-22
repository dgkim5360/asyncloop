from setuptools import setup


def readme():
    with open('README.md') as mdf:
        return mdf.read()


setup(
    name='asyncloop',
    version='0.1.0a1',
    description=(
        'A Celery-like event loop with asyncio '
        'and no more dependencies'
    ),
    long_description=readme(),
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
