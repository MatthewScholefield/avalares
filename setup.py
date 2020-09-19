from setuptools import setup

setup(
    name='avalares',
    version='0.1.3',
    description='Automatic text data extraction tool',
    url='https://github.com/matthewscholefield/avalares',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='avalares',
    packages=['avalares'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'avalares=avalares.__main__:main'
        ],
    }
)
