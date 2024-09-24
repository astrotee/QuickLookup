from setuptools import setup

setup(
    name='QuickLookUp',
    version='0.0.1',
    description='a dictionary app',
    author='Amin Ahmed',
    url='https://github.com/astrotee/QuickLookUp',
    packages=['qlu'],
    install_requires=['Slob >= 1.0'],
    entry_points={'console_scripts': ['qlu=qlu:main']}
)


