"""The module contains an entry point to start http server."""

import argparse
import json
import sys
import webbrowser
from http.server import HTTPServer
from pathlib import Path

from hammett.viz import constants
from hammett.viz.http_server import VizRequestHandler, allocate_port
from hammett.viz.stats import Stats


def parser_builder() -> 'argparse.ArgumentParser':
    """Return configured `ArgumentParser`.

    Returns
    -------
        Configured `ArgumentParser`.

    """
    parser = argparse.ArgumentParser(prog='hammett.viz', usage='%(prog)s [options]')

    parser.add_argument('filepath', help='Stats file, e.g "handler_stats.json"')
    parser.add_argument(
        '-v', '--version', action='version', version=f'%(prog)s {constants.VERSION}',
    )
    parser.add_argument(
        '-H', '--hostname', metavar='HOSTNAME', default='127.0.0.1',
        help='hostname to bind to (default: %(default)s)',
    )
    parser.add_argument(
        '-p', '--port', type=int, metavar='PORT', default=8000,
        help=(
            'port to bind to (default: %(default)s); you can pass the value 0, '
            'then the free port will be selected automatically.'
        ),
    )
    parser.add_argument(
        '-b', '--browser', metavar='BROWSER_NAME',
        help=(
            'name of browser in which it will be opened; '
            'see docs - https://docs.python.org/3/library/webbrowser.html'
        ),
    )

    return parser


def main() -> None:
    """Parse the arguments and start the http server."""
    parser = parser_builder()
    args = parser.parse_args()

    stat_filepath = Path(args.filepath)
    if not stat_filepath.exists():
        parser.error(f"{stat_filepath} doesn't exist")

    if not stat_filepath.is_file():
        parser.error(f"{stat_filepath} isn't a file")

    if not 0 <= args.port <= constants.MAX_PORT_VALUE:
        parser.error(f'{args.port} is out of range')

    with stat_filepath.open('r', encoding='utf-8') as f:
        try:
            stats = json.load(f)
        except json.decoder.JSONDecodeError:
            parser.error(f'{stat_filepath} is not valid JSON file')

    port = args.port if args.port != 0 else allocate_port()

    url = f'http://{args.hostname}:{port}/'
    try:
        browser = webbrowser.get(args.browser)
    except webbrowser.Error as exc:
        parser.error(f'browser not found: {exc}')
    else:
        # if new is 2, a new browser page (“tab”) is opened if possible
        browser.open(url, new=2)

    VizRequestHandler.STATS = Stats(stats)
    server = HTTPServer((args.hostname, port), VizRequestHandler)

    sys.stdout.write(f'Hammett.Viz starting on {url}, press Ctrl+C to exit.\n')
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write('Stopping server...\n')
    finally:
        server.server_close()

    sys.stdout.write('Server stopped\n')


if __name__ == '__main__':
    main()
