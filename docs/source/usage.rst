.. index:: usage


*****
Usage
*****


.. index:: requirements

Requirements
============

In order to use Markdown reveal you need:

- Python 3.5 (or higher).
- `Pandoc <https://pandoc.org/>`_.

And optionally:

- Decktape (``npm install -g decktape``), for exporting to PDF

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
``markdownreveal`` command.

Alternatively, you can use Docker for running ``markdownreveal`` command:

.. code-block:: bash

   docker run -it --rm -p 8123:8123 -v ${PWD}/tmp:/home/mdr/files markdownreveal/markdownreveal -p 8123 -h 0.0.0.0 presentation.md


.. index:: first steps

First steps
===========

Let us create our first presentation! First, we need to create a simple
Markdown file to write our presentation. Let us, for example, create a file
``presentation.md`` and write the following content:

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

Now, while ``markdownreveal`` is running, edit your ``presentation.md`` file
and save the changes. Markdownreveal will automatically refresh your browser
view for you!

.. note:: In case you find the ``markdownreveal`` command too long or tedious
   to write, you can use ``mdr`` instead. Usually the former is used in the
   documentation, but both commands should be considered equivalent.


.. index:: navigation

Navigation
==========

Here is a short list of the keys you can use to navigate these presentations:

- Use ``SPACE`` for next slide.
- Use ``MAYUS + SPACE`` for next slide.
- Use ``ESC`` to visualize the slides grid.
- Use arrows to navigate along the grid.
- Use ``S`` to open the presenter window.

For more information on navigation options, refer to the
`official reveal.js documentation <https://github.com/hakimel/reveal.js/>`_.


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

Numbered lists (note you can use ``1.`` for automatic numbering):

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

Equations (using LaTeX notation):

.. code-block:: bash

    $$
    f(x) = \int_{-\infty}^\infty h(\xi)\,e^{2 \pi i \xi x} \,d\xi
    $$

Also inline equations (using LaTeX notation):

.. code-block:: bash

    Inline equation: $c = \sqrt{a^2 + b^2}$

You may also use Emoji codes!

.. code-block:: bash

    Markdownreveal... :heart_eyes:

For more information, refer to the `official Pandoc documentation
<http://pandoc.org/MANUAL.html#pandocs-markdown>`_.
