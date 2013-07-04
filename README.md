Yota
================

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

**Note: Release of 0.2 has made changes that will minorly break reverse
compatibility. This should be the last time as this code base is maturing, but
be cautious if upgrading any production code to the latest release.**

**Breaking Changes Are:**
+ Validation methods now return a tuple containing (1) Success value (2) Data
  (Json or rendered form).

+ Semantics with which Nodes interact with piecewise validation have changed
  with the re-write, but this only effects people writing custom Nodes.

Getting Started
================

Yota currently provides standard documentation (although is still lacking in some areas) at [ReadTheDocs](https://yota.readthedocs.org/en/latest/).

### [Documentation](https://yota.readthedocs.org/en/latest/)

Example uses in Flask and Django are currently availible in the [Yota Examples](https://github.com/icook/yota_examples>) repository.

### [Examples Repository](https://github.com/icook/yota_examples>)

You can also view our examples live [here](http://64.49.234.90/yota_example).

### [Live Demo](http://64.49.234.90/yota_example)

Get Involved
================

Any and all contributions to Yota are gladly welcomed. Simply fork the
repository and make a pull request with your addition or open an issue for the
maintainers to consider. Please include 100% test coverage with all pull
requests. If you're looking to help out, there are several tickets tagged with
"maintinance" that should be easy starting point. Adding yourself to the
CONTRIBUTORS.txt list when making a pull request is also encouraged.

Latest Changes
================

0.2.1 (2013-07-03)
------------------

### Features

- Added a method to easily change error statuses after validation methods are
  run

### Bug Fixes

- Textarea template whitespace was causing undesirable rendering

- Updated the Button Node to use the proper template inheritence

- Modified insert_validator to accept iterables as the other insert function
  does

- Fixed a documentation bug giving the wrong attribute name for an action

### Maintenance/Stability

- Wrote tests for all new features

- Expanded details in minor places in documentation

- Added checking on attribute name collisions with Nodes to make the mistakes
  easier to debug

Installation
================

Yota has no dependencies on other libraries or packages except for its rendering engine. To install Yota just do:

+ pip install yota jinja2

Or you can install it from Git with:

+ git clone https://github.com/icook/yota.git
+ cd yota
+ pip install .
+ pip install jinja2

License
================

Yota is under the new-style BSD license.

