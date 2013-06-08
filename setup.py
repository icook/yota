import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
]

setup(name='yota',
      version='0.1.2',
      description='A form library with a focus on simplicity',
      long_description="",
      author='',
      url='',
      packages=find_packages('src'),
      include_package_data=True,
      install_requires=requires,
      package_dir = {'': 'src'},
      )
