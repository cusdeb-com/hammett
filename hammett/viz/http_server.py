"""The module contains the http server handler."""

import re
import socket
from contextlib import closing
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, cast

from hammett.viz.stats import avg_stats_table_rows
from hammett.viz.template import Template

if TYPE_CHECKING:
    from typing import Any

    from hammett.viz.stats import Stats


def allocate_port() -> int:
    """Allocate a free port and return it.

    Returns
    -------
        Allocated port.

    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('', 0))
        return cast('int', sock.getsockname()[1])


class VizRequestHandler(SimpleHTTPRequestHandler):
    """Viz HTTP request handler."""

    STATS: 'Stats | None' = None
    directory_path = Path.cwd() / 'hammett' / 'viz'

    def __init__(self, *args: 'Any', **kwargs: 'Any') -> None:
        """Set the working directory with templates and static files."""
        kwargs['directory'] = f'{self.directory_path}'
        super().__init__(*args, **kwargs)

    def _send_headers(self) -> None:
        """Send headers and closes their sending."""
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def process_static_file(self) -> None:
        """Process a request for static files."""
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)  # type: ignore[misc]
            finally:
                f.close()

    def index(self) -> None:
        """Render index page and write it to response.

        Raises
        ------
            RuntimeError: If the Stats object is not available.

        """
        if self.STATS is None:
            msg = 'Stats is not available'
            raise RuntimeError(msg)

        stat_table = avg_stats_table_rows(self.STATS.avg_stats)
        template_path = self.directory_path / 'templates' / 'index.html'
        template = Template(template_path).load().render(stat_table=stat_table)
        self.copyfile(BytesIO(template), self.wfile)  # type: ignore[misc]

    def do_GET(self) -> None:
        """Handle GET requests to the web server."""
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self._send_headers()
            return self.index()
        if re.match(r'^/static', self.path):
            return self.process_static_file()
        if re.match(r'^/favicon.ico', self.path):
            self.path = '/static/favicon.ico'
            return self.process_static_file()

        self.send_error(HTTPStatus.NOT_FOUND)
        return None
