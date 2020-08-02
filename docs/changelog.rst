=========
Changelog
=========

* :support:`125` Fix long_description for PyPI
* :release:`0.12.0 <2020-05-23>`
* :support:`120` Upgrade to python 3.8
* :support:`119` Upgrade to pandas 1.0
* :feature:`50` Add a distutils command for marbles
* :release:`0.11.0 <2019-11-17>`
* :feature:`107` Allow triple-quoted annotations to be indented in source
* :support:`105` Fixed ``UniqueMixins`` literalinclude line numbers in docs
* :support:`101` Added note about how to execute logging configured tests
* :support:`99` Fixed ``assertCategoricalLevel(Not)In`` docstring parameters
* :release:`0.10.0 <2018-09-23>`
* :feature:`92` Improve indentation of multiline locals
* :support:`90` Added support for python 3.7
* :support:`88` Document how to install with conda
* :release:`0.9.5 <2018-06-24>`
* :support:`80` Added support for ``pandas<0.24``
* :bug:`58` Fixed test failure on OSX
* :release:`0.9.4 <2018-06-03>`
* :bug:`65` Fixed sdist installation
* :release:`0.9.3 <2018-06-02>`
* :support:`43` Added version bumping automation and maintenance documentation
* :support:`39` Added issue templates
* :bug:`40` Fixed "Locals" section in failure output to be hidden when
  no locals will be displayed
* :bug:`41` Removed developer dependencies in ``setup_requires`` and
  ``tests_require``
* :release:`0.9.2 <2018-05-19>`
* :support:`0`

  .. note:: First public release

* :support:`31` Added PyPI packaging
* :support:`28` Added Travis CI integration
* :support:`26` Added development automation and CI with tox
* :support:`17` Changed to pipenv for development environment management
* :support:`16` Added Contributor License Agreement forms
* :bug:`15` Added Creative Commons attribution for test content from Wikipedia
* :bug:`5` Changed copyright headers to refer to TSOS and the MIT license
* :bug:`1` Fixed tests to run in virtualenvs
* :support:`14` Removed DataFrame and Panel mixins
* :support:`18` Removed TS internal details from README
* :support:`21` Removed TS internal details from documentation and comments
* :support:`30` Removed TS internal conda recipe
* :release:`0.8.0 <2018-05-18>`
* :feature:`0` Large refactor and doc rewrite to prepare for open source
* :feature:`0` Added main method to provide ``python -m marbles``
* :support:`0` Split package into ``marbles.core`` and ``marbles.mixins``
* :feature:`0` Removed Traceback display for marbles assertion failures
* :feature:`0` Changed annotation to be optional with ``marbles.core.TestCase``
* :feature:`0` Changed test case and test method to log separately,
  and added marbles version
* :release:`0.6.9 <2017-10-18>`
* :support:`0`

  .. admonition:: Nice

     Nice

* :support:`0` Added conda recipe (internal only)
* :bug:`0` Fixed mixins that expect a specific type to raise
  ``TypeError`` instead of ``AssertionError``
* :bug:`0` Fixed source code extraction to find it inside eggs
* :release:`0.6.0 <2017-08-10>`
* :feature:`0` Added verbose logging option
* :feature:`0` Changed annotation wrapping to wrap paragraphs in
  annotations individually for better formatting
* :release:`0.5.0 <2017-03-20>`
* :feature:`0` Added mixins library
* :feature:`0` Added documentation about authoring good marbles docs
* :release:`0.4.0 <2017-02-28>`
* :feature:`0` Added richer text formatting in annotations
* :release:`0.3.0 <2017-02-23>`
* :feature:`0` Added assertion logging
* :release:`0.2.0 <2016-12-14>`
* :bug:`0` Fixed positional argument handling
* :feature:`0` Removed display of "private" locals
* :feature:`0` Removed extra ``message`` annotation
* :release:`0.1.0 <2016-10-19>`
* :feature:`0` Added annotation support in ``assert*`` methods
* :feature:`0` Added source code for the whole statement that failed
  to failure messages
* :feature:`0` Added ability to capture and display locals
