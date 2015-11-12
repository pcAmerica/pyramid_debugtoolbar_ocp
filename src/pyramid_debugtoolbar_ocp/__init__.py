__version__ = "15.1.0"

__title__ = "pyramid_debugtoolbar_ocp"
__description__ = "OCP pyramid debug toolbar customizations"
__uri__ = "https://github.com/pcamerica/pyramid_debugtoolbar_ocp"

__author__ = "Lucas Taylor"
__email__ = "lucas.taylor@e-hps.com"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2015 {0}".format(__author__)



def includeme(config):
    """
    Remove default SQLAlchemy panel and insert the OCP SQLAlchemy panel
    in its place.
    """
    from pyramid_debugtoolbar.panels.sqla import (SQLADebugPanel,
        _before_cursor_execute, _after_cursor_execute)
    from sqlalchemy.engine.base import Engine
    from sqlalchemy import event

    from .panels.sqla import OCPSQLADebugPanel

    # Remove event listeners registered by the original SQLAlchemy panel
    event.remove(Engine, 'before_cursor_execute', _before_cursor_execute)
    event.remove(Engine, 'after_cursor_execute', _after_cursor_execute)

    panels = config.registry.settings['debugtoolbar.panels']

    idx = -1
    if SQLADebugPanel in panels:
        idx = panels.index(SQLADebugPanel)
        del panels[idx]

    panels.insert(idx, OCPSQLADebugPanel)
