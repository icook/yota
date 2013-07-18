import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'jinja2'
]

testing_extras = ['nose', 'coverage', 'beautifulsoup4']
docs_extras = ['Sphinx', 'sphinxcontrib-fulltoc']

try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except:
    README = ''

setup(name='yota',
      version='0.2.1',
      description='A form library with a focus on simplicity',
      long_description=README,
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: Implementation :: CPython"
      ],
      license='LICENSE',
      tests_require=testing_extras,
      author='Isaac Cook',
      author_email="yota-discuss@googlegroups.com",
      url='https://github.com/icook/yota',
      packages=find_packages('src'),
      include_package_data=True,
      install_requires=requires,
      test_suite='yota.tests',
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
      },
      package_dir={'': 'src'}
      )
