.. index:: developers


**********
Developers
**********


.. index::
    double: developers; dependencies

Installing dependencies
=======================

To install the required dependencies for developing Markdownreveal, you can
make use of the provided `requirements.txt` file:

.. code-block:: bash

   pip install -r requirements.txt


.. index::
    double: developers; tests

Running tests
=============

Running the tests locally is very simple, using
`Tox <https://tox.readthedocs.io/>`_ from the top level path of the project:

.. code-block:: bash

   tox

That single command will run all the tests for all the supported Python
versions available in your system or environment.

For faster results you may want to run all the tests just against a single
Python version. This command will run all tests against Python 3.5 only:

.. code-block:: bash

   tox -e py35

Note that those tests include style and static analysis checks. If you just
want to run all the behavior tests (not recommended):

.. code-block:: bash

   pytest -n 8

If you just want to run a handful of behavior tests (common when developing
new functionality), just run:

.. code-block:: bash

   pytest -k keyword

.. note:: Before submitting your changes for review, make sure all tests pass
   with `tox`, as the continuous integration system will run all those checks
   as well.


.. index::
    double: developers; documentation


Generating documentation
========================

Documentation is generated with Sphinx. In order to generate the documentation locally you need to run `make` from the `docs` directory:

.. code-block:: bash

   make html
