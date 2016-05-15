try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name="ereb",
    version="0.1",
    author="aviasales",
    author_email="devs@aviasales.ru",
    packages=find_packages(),
    scripts=['bin/ereb'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        ],
    install_requires=[
         "tornado>=4.2",
         "crontab>=0.21",
         "psutil>=4.1",
    ],
    tests_require=[],
    )
