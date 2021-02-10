# Automatically created by: scrapyd-deploy

from setuptools import find_packages, setup

setup(
    name='demo',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = demo.settings']},
    install_requires=[
        'scrapy>=1.5.1',
        'flask',
        'requests'
    ]
)
