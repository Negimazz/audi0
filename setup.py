from setuptools import setup, find_packages

setup(
    name='audi0',
    version='0.1.0',
    py_modules=['visualizer'],
    entry_points={
        'console_scripts': [
            'audi0=visualizer:main',
        ],
    },
    install_requires=[
        'numpy',
        'colorama',
        'pyaudiowpatch; sys_platform=="win32"',
        'pyaudio; sys_platform!="win32"'
    ],
)
