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
- Internet access.

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


.. index:: navigation

Navigation
==========

Here is a short list of the keys you can use to navigate these presentations:

- Use `SPACE` for next slide.
- Use `MAYUS + SPACE` for next slide.
- Use `ESC` to visualize the slides grid.
- Use arrows to navigate along the grid.
- Use `S` to open the presenter window.

For more information on navigation options, refer to the
`official documentation <https://github.com/hakimel/reveal.js/>`_.


.. index:: notation

Notation
========

The presentation should start with the title, author and date:

.. code-block:: bash

    % Presentation title
    % Author
    % YYYY-MM-DD

You can create vertical sections in your presentation using titles:

.. code-block:: bash

    # New section

New slides in a section using subtitles:

.. code-block:: bash

    ## Subtitle

Simple paragraphs with text lines:

.. code-block:: bash

    This is a paragraph.

Simple lists:

.. code-block:: bash

    - List item.
    - Another one.

Numbered lists (note you can use `1.` for automatic numbering):

.. code-block:: bash

    1. First item.
    1. Second item.

Force the creation of a new slide:

.. code-block:: bash

    ---

Code (with optional syntax highlighting):

.. code-block:: bash

    ```python
    print('Hello world!')
    ```

Images (with optional width):

.. code-block:: bash

    ![Alt text](./figures/yourfigure.png){width=70%}

For more information, refer to the
`official documentation <http://pandoc.org/MANUAL.html#pandocs-markdown>`_.
