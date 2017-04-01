.. index:: style


*****
Style
*****


.. index::
    double: footer; header

Footer and header
=================

You can very easily add a footer and/or a header to your slides with
Markdownreveal. Try to create a file `config.yaml` and write the following:

.. code-block:: bash

   footer: 'My footer | www.mywebsite.com'

You should now see a footer in all your slides. Use `header` to add a header
too or instead.


.. index::
    double: style; default

Using reveal.js themes
======================

We think the default Markdownreveal theme is okay, but to each their own...
If you would rather use the default reveal.js themes, you can do so in a very
easy way. In your `config.yaml` file, try to add:

.. code-block:: bash

   style: ''

What you see now is the `white` reveal.js style. You can also change that
parameter if you want. Try:

.. code-block:: bash

   theme: 'moon'


.. warning:: Note that when using reveal.js themes, `footer` and `header`
   will not work as they are not defined in the default reveal.js CSS files.


.. index::
    double: style; own

Creating your own style
=======================

You can definitely create your own style too! To do so, create a folder named
`style` in your presentation root directory. You can add the following files
in there:

- `background.svg`: an image to be used as a background.
- `logo.svg`: a logo to display on your slides on a corner.
- `warmup.svg`: an image to be displayed before the presentation title.
- `custom.css`: your CSS rules for your own style.
- `config.yaml`: to tune the style default configuration (footer, header...).

You can check the `Markdownreveal style repository
<https://github.com/markdownreveal/style-default>`_ to get an idea on how to
create the CSS file. Note that your custom style will be based on reveal.js's
`white` theme.


.. index::
    double: style; repository

Using your style repository
===========================

If you are doing many presentation, or if you work for a company, you may
find it useful to create your own style repository. Simply upload your files
to a repository, as `we do ourselves with Markdownreveal
<https://github.com/markdownreveal/style-default>`_ and then edit your
`config.yaml` file:

.. code-block:: bash

    style: 'https://github.com/markdownreveal/style-default/archive/master.tar.gz'

Put there an URL pointing to your style files. Note that they need to be
contained in a `tar.gz` file.
