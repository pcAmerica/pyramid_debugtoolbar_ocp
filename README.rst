*******************************
OCP Pyramid Debugtoolbar Panels
*******************************

``pyramid_debugtoolbar_ocp`` contains customizations to the default
``pyramid_debugtoolbar`` that are specific to the OnCloudPortal project.

Configuration
=============

Include the package after including ``pyramid_debugtoolbar``

.. code-block:: python

    config.include('pyramid_debugtoolbar')
    config.include('pyramid_debugtoolbar_ocp')


Features
========

SQLA (OCP)

Forked SQLAlchemy panel to modify output and fix some issues.

* Output includes the name or id of the db engine used to execute the
  query. Useful to distinguish between different engines used
  (primary for auth, etc., cubes for reporting queries)

* OCP generates child db engines for each customer schema to be used for
  cubes/reporting queries. This causes the ``after_cursor_execute`` event
  to be fired twice, duplicating query output in the panel and triggering
  an exception due to a missing attribute on the connection.

  This panel works around the issue by disregarding any connections that
  are missing a starting timer value.

  The issue is similar to
  https://github.com/Pylons/pyramid_debugtoolbar/issues/65

