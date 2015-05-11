#!/usr/bin/python 
from setuptools import setup

setup(name='serfcommonpatterns',
      version='0.1',
      description='Common programming patterns using serf',
      url='http://github.com/JosiahKerley/serf-common-patterns',
      author='Josiah Kerley',
      author_email='josiahkerley@gmail.com',
      install_requires=['serfclient'],
      license='MIT',
      packages=['serfcommonpatterns'],
      zip_safe=False,)