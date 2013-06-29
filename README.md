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
maintainers to consider. If you're looking to help out, there are several
tickets tagged with "maintinance" that can be completed. Adding yourself to the
CONTRIBUTORS.txt list when making a pull request is also encouraged.

Latest Changes
================

0.2.0 (2013-06-28)
------------------

### Features

- Added some more built-in Nodes and Validators such as
  StrongPasswordValidator, MatchingValidator, RegexValidator, CheckboxNode,
  etc.

- Refactored all validation functions to return both a success bool value
  alongside its output, making post-validation logic more clear and concise.

### Refactor for Client Side Funcionality

- Completely re-wrote the JavaScript library into a jQuery plugin.

- Moved the selection loigc for Nodes that are "ready" to be validated into
  server side, incurring marginal overheads.

- Changed the error_render call semantics to track which Nodes have errors and
  intelligently call the function.

- Improved error rendering to support multiple errors.

- Re-designed the semantic which finds the HTML node in which to place errors
  on a per Node basis. json_identifiers function now passes these details to
  the client side code allowing more flexible rendering.

- Allowed per-Node logic for deciding if the Node is ready to be validated
  based on a list of visited Nodes.

- Added a more robust render_success method that allows passing arbitrary
  information to drive things like redirects, etc.

### Documentation

- Large expansions in the documentation in almost all areas. More should be
  coming steadily in the next few weeks.

- Re-wrote the yota_examples repository for improved clarity and commenting.

### Maintenance/Stability

- Introduced simple functional tests to attempt coverage for behaviour that
  cannot be unit tested

- Added commenting and specificity to existing unit tests

- Added more unit tests to regain near 100% coverage. Touch ups to come soon.

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

