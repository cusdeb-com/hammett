"""Entry-point for the `hammett.viz` command."""

import sys

if __name__ == '__main__':
    from hammett.viz.main import main
    sys.exit(main())  # type: ignore[func-returns-value]
