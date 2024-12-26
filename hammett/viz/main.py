"""The module contains an entry point to start http server."""

import argparse
import sys
import webbrowser
from http.server import HTTPServer
from pathlib import Path

from hammett.viz import constants
from hammett.viz.color import Style, colorize
from hammett.viz.http_server import VizRequestHandler, allocate_port
from hammett.viz.stats import detect_stats_files, get_platforms


def parser_builder() -> 'argparse.ArgumentParser':
    """Return configured `ArgumentParser`.

    Returns
    -------
        Configured `ArgumentParser`.

    """
    parser = argparse.ArgumentParser(prog='hammett.viz', usage='%(prog)s [options]')

    parser.add_argument(
        'directory',
        help=(
            'directory that contains files '
            'such as "handler-stats-87181a567d439062fcd6d94cc194a8b7.json"'
        ),
    )
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

    dir_path = Path(args.directory)
    if not dir_path.exists():
        parser.error(f"{dir_path} doesn't exist")

    if not dir_path.is_dir():
        parser.error(f"{dir_path} isn't a directory")

    if not 0 <= args.port <= constants.MAX_PORT_VALUE:
        parser.error(f'{args.port} is out of range')

    stats_files = detect_stats_files(dir_path)
    if not stats_files:
        sys.stdout.write(colorize(
            Style.WARNING,
            'No files with statistics found in the directory\n',
        ))

    VizRequestHandler.platforms = get_platforms(stats_files)
    port = args.port if args.port != 0 else allocate_port()

    url = f'http://{args.hostname}:{port}/'
    try:
        browser = webbrowser.get(args.browser)
    except webbrowser.Error as exc:
        parser.error(f'browser not found: {exc}')
    else:
        # if new is 2, a new browser page (“tab”) is opened if possible
        browser.open(url, new=2)

    server = HTTPServer((args.hostname, port), VizRequestHandler)

    sys.stdout.write(colorize(
        Style.SUCCESS,
        f'Hammett.Viz starting on {url}, press Ctrl+C to exit.\n',
    ))
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write('Stopping server...\n')
    finally:
        server.server_close()

    sys.stdout.write('Server stopped\n')


if __name__ == '__main__':
    main()
