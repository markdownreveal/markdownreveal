.. index:: subcommands


***********
Subcommands
***********


.. index:: list

List subcommands
================

Markdownreveal provides a couple of subcommands for convenience. If you want
to list those commands, you can use the ``--help`` option:

.. code-block:: bash

   markdownreveal --help

.. note:: There is one subcommand called ``show``, which is the default when
   no subcommand is specified. This subcommand will, as you already know,
   open your web browser to visualize your presentation.


.. index:: share

Share your presentation
=======================

If you want to share your presentation with somebody, or if you want to upload
it to a server, you can use the ``zip`` subcommand:

.. code-block:: bash

   markdownreveal zip presentation.md

This will create a ZIP file containing your presentation. Note that the
presentation is a static webpage, so in order to open it you just need to
double-click on ``index.html`` and you can easily upload it to your own server
if that is what you need.


.. index:: clean, local

Clean local files
=================

Markdownreveal downloads reveal.js and style files and saves them locally for
future use. If you want to remove those files, you can make use of the
``clean`` subcommand:

.. code-block:: bash

   markdownreveal clean
