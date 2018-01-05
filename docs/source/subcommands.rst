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


.. index:: show

Show your presentation
======================

If you want to visualize your presentation you need to use the subcommand
``show``. This is the default when no subcommand is specified, which means
that this:

.. code-block:: bash

   markdownreveal presentation.md

Is equivalent to:

.. code-block:: bash

   markdownreveal show presentation.md

.. note:: This subcommand also accepts two options: ``--port`` and ``--host``
   to change the default port and host where the presentation will be served
   on. See ``markdownreveal show --help`` for more information.


.. index:: share

Share your presentation
=======================

If you want to share your presentation with somebody, or if you want to upload
it to a server, you can use the ``zip`` subcommand:

.. code-block:: bash

   markdownreveal zip presentation.md

This will create a ZIP file containing your presentation. Note that the
presentation is a static webpage, so in order to view it you just need to open
``index.html`` with your web browser. You can also upload it to your own server
if you prefer so.


.. index:: github, pages

GitHub pages
============

If you happen to be using GitHub to host your presentation code, then sharing
could not be simpler. You can use the subcommand ``upload`` to upload your
presentation to GitHub pages:

.. code-block:: bash

   markdownreveal upload presentation.md

.. warning:: Note that executing this command will reset the branch
   ``gh-pages``, so make sure your repository holds your presentation only or
   you are not using that branch.

.. note:: You can use the ``--remote`` option to change the default remote
   where the presentation will be uploaded to. See ``markdownreveal upload
   --help`` for more information.


.. index:: export, pdf

Export to PDF
=============

You can also export your presentation to PDF. This functionality, however,
requires `Docker <https://www.docker.com/>`_, so you need to have it installed
and configured in your system.

In order to export your presentation to PDF, use the ``pdf`` subcommand and
provide the URL where your presentation is being served (either the server
where you uploaded it or the local server that is spawned when you run
Markdownreveal locally and the presentation is opened in your browser:

.. code-block:: bash

   markdownreveal pdf http://localhost:8123/#/

A PDF file will be created in the current directory with the presentation.

.. note:: Docker was chosen for convenience and security. Exporting the
   presentation to PDF requires tools that otherwise would need to be
   installed as binaries (insecure) or compiled (inconvenient).

   Currently the export process uses
   `DeckTape <https://github.com/astefanutti/decktape>`_ and a patched
   `PhantomJS <https://github.com/ariya/phantomjs>`_ version. If, at some
   point, DeckTape is able to work with a non-patched PhantomJS version, we
   may consider adding support for export without Docker.

   For exporting the presentation, Docker is given access only to a temporary
   folder where it can write the PDF output. Then Markdownreveal copies this
   file to the current directory once the export is finished.


.. index:: clean, local

Clean local files
=================

Markdownreveal downloads reveal.js and style files and saves them locally for
future use. If you want to remove those files, you can make use of the
``clean`` subcommand:

.. code-block:: bash

   markdownreveal clean
