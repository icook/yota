.. image:: https://travis-ci.org/icook/yota.png?branch=master
    :target: https://travis-ci.org/icook/yota
.. image:: https://coveralls.io/repos/icook/yota/badge.png?branch=master
    :target: https://coveralls.io/r/icook/yota?branch=master

Yota
================

*************************************************************************************************************************************************************************************
`Documentation <https://yota.readthedocs.org/en/latest/>`_ | `Example Repository <https://github.com/icook/yota_examples>`_ | `Demo <http://yota.ibcook.com/>`_
*************************************************************************************************************************************************************************************

Yota is a Python form generation library with the following unique features:

+ Easy integration of realtime validation. Trigger a server side form
  validation with any JavaScript event on your input fields. (Client side in
  planning)

+ Dynamic form structures allow for complex forms with on the fly changes.
  Inject different input fields or validation methods into a specific instance
  of your Form where needed.

+ Default themed with Bootstrap, allowing you to quickly throw together useful
  forms that look nice.

In addition to these features, Yota also includes most of the features that
you would see with other form libraries.

+ Simple declarative syntax for defining form validation and layout

+ Customizable template driven schemas

+ Ability to operate with almost any framework and use any rendering engine.
  (Default is jinja2)

Philosophically Yota aims to have a ton of power, since designing Forms can
require a lot of flexibility. This was the main problem the designers had with
other libraries is that they ended up getting in the way. At the same time
however it is important that sensible default be easy to use and implement,
making the creation of common forms trivial and lowering the inital learning
curve.

Installation
================

To install Yota just:

+ pip install yota

Or you can install it from Git with:

+ git clone https://github.com/icook/yota.git
+ cd yota
+ pip install .
+ pip install jinja2

Tests
================

Yota tries hard to maintain a high level of test coverage, and as such running 
the tests before pull requests and commits is important. Tests are setup to run
with nose, and some testing parses HTML with beautifulsoup. To install:

+ pip install nose beautifulsoup4

Then run:

+ nosetests

in the root folder of the project.

Get Involved
================

Any and all contributions to Yota are gladly welcomed. Simply fork the
repository and make a pull request with your addition or open an issue for the
maintainers to consider. Please include 100% test coverage with all pull
requests. If you're looking to help out, there are several tickets tagged with
"maintinance" that should be easy starting point. Adding yourself to the
CONTRIBUTORS.txt list when making a pull request is also encouraged.

Latest Changes
============================

*******************
0.2.2 (2013-08-22)
*******************

Features
------------------

- Added post-success JavaScript hooks for common actions as well as custom JS

- Shorthand validation is now allowed for dynamically inserted nodes

- Added Python 3.3 support

- Implemented a 'validator' method for Form that allows one-off validation for 
  validation logic that is specific to that form only

- Added new 'render_success' and 'error_success' attributes for Form to specify
  a JavaScript function to replace the default callback in the JS api
  
- css_style, disable, and css_class are now Node attributes that can be used in
  templates

- Added a new FileNode for uploading files with along with a MimeTypeValidator
  and associated template modifications

Bug Fixes
----------

- Documentation fixes

- Setting title=False didn't function correctly

- Some class attribute override semantics didn't function as intended and have
  now been resolved

- Fixed a unicode encoding error identified by xen that was breaking validation

Maintenance/Stability
----------------------

- Moved some functionality out of the metaclass to be more lazy, increasing the
  initialization speed of classes and improving testing

- Wrote many additional tests and significantly improved assertion coverage

- Completely re-organized tests to be organized less haphazzardly and updated 
  /extended their comments significantly.

- Setup coveralls and Travis CI

- Gave the whole codebase a PyLint and PEP8 pass

License
================

Yota is under the new-style BSD license.
