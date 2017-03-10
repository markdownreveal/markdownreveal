.. index:: usage


*****
Usage
*****


.. index:: requirements

Requirements
============

In order to use Markdown reveal you need:

- `Pandoc <https://pandoc.org/>`_ installed in your system.
- A Python 3.5 (or higher) interpreter.
- Permissions to install the package with `pip`.

.. note:: Windows and Mac platforms are theoretically supported, but not
   currently tested by developers. For those platforms you may not even need
   to manually install Pandoc, as it should be automatically installed.


.. index:: installation

Installation
============

Installation is very straight-forward:

.. code-block:: bash

   pip install markdownreveal

This will install all the required dependencies and will provide you with the
`markdownreveal` command.


.. index:: first steps

First steps
===========

Let us create our first presentation! First, we need to create a simple
Markdown file to write our presentation. Let us, for example, create a file
`presentation.md` and write the following content:

.. code-block:: markdown

    % Presentation title
    % Author
    % YYYY-MM-DD

    # First section

    ## Subsection

    This is my first Markdownreveal presentation.

Now, simply execute:

.. code-block:: bash

   markdownreveal presentation.md

If everything went well a new tab should be opened in your browser showing
you the presentation.

Now, while `markdownreveal` is running, edit your `presentation.md` file
and save the changes. Markdownreveal will automatically refresh your browser
view for you!
