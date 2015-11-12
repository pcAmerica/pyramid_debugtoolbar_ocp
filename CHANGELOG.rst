*********
Changelog
*********

Versions are year-based. The second digit is incremented per-release and
the third digit is used for regressions.

15.1.0 (2015-11-12)
===================

Changes:
--------

- No longer rely on existence of ``cubes_engines`` dict in ``sqla_engines``
  All sqlalchemy engines should be registered in ``registry.sqla_engines``
- Gracefully degrade if ``sqla_engines`` dict is not in the registry
  (panel will display the object id of the engine instead)



15.0.0 (2015-11-12)
===================

Changes:
--------

- Initial release.
