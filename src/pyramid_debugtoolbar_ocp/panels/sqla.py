"""
OCP SQLAlchemy debug toolbar panel

- Provides named db engine in output to distinguish between cubes and
  primary db engine
- Workaround for race condition in debugtoolbar. Multiple queries are
  issued on the same connection and cursor, leading to a problem
  discovering timings.
  https://github.com/Pylons/pyramid_debugtoolbar/issues/65
"""
from __future__ import with_statement

import hashlib
import threading
import time
import weakref

from pyramid.threadlocal import get_current_request

from pyramid_debugtoolbar.compat import json
from pyramid_debugtoolbar.compat import bytes_
from pyramid_debugtoolbar.compat import url_quote
from pyramid_debugtoolbar.compat import PY3
from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import format_sql
from pyramid_debugtoolbar.utils import STATIC_PATH
from pyramid_debugtoolbar.utils import ROOT_ROUTE_NAME

lock = threading.Lock()

def text(s):
    if PY3: # pragma: no cover
        return str(s)
    else:
        return unicode(s)

try:
    from sqlalchemy import event
    from sqlalchemy.engine.base import Engine

    @event.listens_for(Engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, stmt, params, context, execmany):
        conn.info['ocp_pdtb_start_timer'] = time.time()

    @event.listens_for(Engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
        if not conn.info.get('ocp_pdtb_start_timer'):
            return

        stop_timer = time.time()
        request = get_current_request()

        if request is not None and hasattr(request, 'ocp_pdtb_sqla_queries'):
            with lock:
                engines = request.registry.pdtb_sqla_engines
                engines[id(conn.engine)] = weakref.ref(conn.engine)
                queries = request.ocp_pdtb_sqla_queries

                ocp_engines = getattr(request.registry, 'sqla_engines', {})
                ocp_named_engines = dict([(id(v), k) for k, v in ocp_engines.items()])

                duration = (stop_timer - conn.info.get('ocp_pdtb_start_timer', 0)) * 1000

                queries.append({
                    'engine_id': id(conn.engine),
                    'engine': ocp_named_engines.get(id(conn.engine), id(conn.engine)),
                    'duration': duration,
                    'statement': stmt,
                    'parameters': params,
                    'context': context
                })

        conn.info.pop('ocp_pdtb_start_timer', None)

    has_sqla = True
except ImportError:
    has_sqla = False

_ = lambda x: x


class OCPSQLADebugPanel(DebugPanel):
    """
    Panel that displays the SQL generated by SQLAlchemy plus the time each
    SQL statement took in milliseconds.
    """
    name = 'SQLAOCP'
    template = 'pyramid_debugtoolbar_ocp.panels:templates/sqlalchemy.dbtmako'
    title = _('SQLAlchemy Queries')
    nav_title = _('SQLA (OCP)')

    def __init__(self, request):
        self.queries = request.ocp_pdtb_sqla_queries = []
        if hasattr(request.registry, 'pdtb_sqla_engines'):
            self.engines = request.registry.pdtb_sqla_engines
        else:
            self.engines = request.registry.pdtb_sqla_engines = {}
        self.token = request.registry.pdtb_token

    @property
    def has_content(self):
        if self.queries:
            return True
        else:
            return False

    @property
    def nav_subtitle(self):
        if self.queries:
            return "%d" % (len(self.queries))

    def process_response(self, response):
        data = []

        for query in self.queries:
            stmt = query['statement']

            is_select = stmt.strip().lower().startswith('select')
            params = ''
            try:
                params = url_quote(json.dumps(query['parameters']))
            except TypeError:
                pass # object not JSON serializable
            except UnicodeDecodeError:
                pass # parameters contain non-utf8 (probably binary) data

            need = self.token + stmt + params
            hash = hashlib.sha1(bytes_(need)).hexdigest()

            data.append({
                'engine_id': query['engine_id'],
                'engine': query['engine'],
                'duration': query['duration'],
                'sql': format_sql(stmt),
                'raw_sql': stmt,
                'hash': hash,
                'parameters': query['parameters'],
                'params': params,
                'is_select': is_select,
                'context': query['context'],
            })

        self.data = {
            'queries':data,
            'text':text,
            }

    def render_content(self, request):
        if not self.queries:
            return 'No queries in executed in request.'
        return super(OCPSQLADebugPanel, self).render_content(request)

    def render_vars(self, request):
        return {
            'static_path': request.static_url(STATIC_PATH),
            'root_path': request.route_url(ROOT_ROUTE_NAME)
        }
