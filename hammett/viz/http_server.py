"""The module contains the http server handler."""

import re
import socket
from contextlib import closing
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, cast

from hammett.viz.stats import Stats, avg_stats_table_rows
from hammett.viz.template import Template

if TYPE_CHECKING:
    from typing import Any


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

    platforms: dict[str, tuple[str, Path]] = {}
    directory_path = Path.cwd() / 'hammett' / 'viz'

    def __init__(self, *args: 'Any', **kwargs: 'Any') -> None:
        """Set the working directory with templates and static files."""
        kwargs['directory'] = f'{self.directory_path}'

        self.cur_platform = ''
        if self.platforms:
            # it's ok on python 3.7+ where dicts are ordered
            self.cur_platform = next(iter(self.platforms))

        super().__init__(*args, **kwargs)

    @staticmethod
    def _parse_platform_name(raw_platform_name: str) -> tuple[str, str]:
        """Return the readable names of the platform.

        Returns
        -------
            Readable names of the platform.

        """
        platform_list = raw_platform_name.split(';')
        platform_fullname = ' '.join(platform_list)
        platform = platform_list[0]
        return platform, platform_fullname

    def _render_platforms(self) -> str:
        """Return HTML links to other platforms.

        Returns
        -------
            HTML links to other platforms.

        """
        platforms = ''
        for platform_hash, (raw_platform_name, _) in self.platforms.items():
            classes = ['tab', 'active'] if self.cur_platform == platform_hash else ['tab']

            platform, platform_fullname = self._parse_platform_name(raw_platform_name)
            platforms += (
                f'<a href="/stats/{platform_hash}" class="{" ".join(classes)}" '
                f'title="{platform_fullname}">'
                f'{platform}</a>\n'
            )

        return platforms

    def _send_headers(self) -> None:
        """Send headers and closes their sending."""
        self.send_header('Content-Type', 'text/html')
        self.send_header('Last-Modified', self.date_time_string())
        self.end_headers()

    def process_static_file(self) -> None:
        """Process a request for static files."""
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def index(self) -> None:
        """Render index page and write it to response."""
        stat_table = ''
        if self.platforms and self.cur_platform:
            _, file_path = self.platforms[self.cur_platform]

            avg_stats = Stats(file_path).load().avg_stats()
            stat_table = avg_stats_table_rows(avg_stats)

        template_path = self.directory_path / 'templates' / 'index.html'
        template = Template(template_path).load().render(
            stat_table=stat_table,
            platforms=self._render_platforms(),
        )
        self.copyfile(BytesIO(template), self.wfile)

    def do_GET(self) -> None:
        """Handle GET requests to the web server."""
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self._send_headers()
            return self.index()
        if re.match(r'^/stats/\w{32}', self.path):
            try:
                self.cur_platform = re.findall(r'\w{32}', self.path)[0]
            except IndexError:
                self.send_error(HTTPStatus.NOT_FOUND)
                return None
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
