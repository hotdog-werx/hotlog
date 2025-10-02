"""Quick Start Guide for hotlog.

This example shows the most common patterns you'll use:
1. Simple info messages
2. Messages with highlighted values
3. Prefix filtering (_verbose_, _debug_)
4. Tool execution pattern with ToolMatch
5. Live logging for long operations

Run with: python example_quickstart.py [-v|-vv]
"""

import argparse
import os
import sys
import time
from textwrap import dedent

from hotlog import (
    ToolMatch,
    configure_logging,
    get_logger,
    highlight,
    live_logging,
)


def _sleep(seconds: float) -> None:
    """Sleep for the given time, unless HOTLOG_NO_DELAY is set."""
    if os.environ.get('HOTLOG_NO_DELAY'):
        return
    time.sleep(seconds)


def main() -> None:
    """Run the quickstart example."""
    parser = argparse.ArgumentParser(
        description='Quick start examples for hotlog',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for verbose, -vv for debug)',
    )
    args = parser.parse_args()

    verbosity = args.verbose

    # Configure with ToolMatch for your project
    configure_logging(
        verbosity=verbosity,
        matchers=[ToolMatch(event='executing', prefix='myapp')],
    )
    logger = get_logger(__name__)

    header = dedent(f"""
        ============================================================
        Quick Start Example (verbosity level: {verbosity})
        ============================================================
    """)
    sys.stdout.write(header)

    # 1. Simple messages
    logger.info('Application starting', version='1.0.0')

    # 2. Messages with highlighted values (like uv)
    logger.info(highlight('Loaded {} in {}', '50 plugins', '120ms'))

    # 3. Prefix filtering - automatic based on verbosity
    logger.info(
        'Configuration loaded',
        env='production',
        _verbose_config_file='/etc/myapp/config.yaml',
        _debug_raw_config={'key': 'value'},
    )

    # 4. Tool execution - automatic formatting
    logger.info(
        'executing',
        command='docker build -t myapp:latest .',
        tool='docker-build',
        _verbose_layers=12,
        _debug_build_context='~/builds/build-123',
    )

    # 5. Live logging for long operations
    with live_logging('Downloading dependencies...') as live:
        for i in range(1, 4):
            _sleep(0.3)
            live.info(f'Downloaded package-{i}', _verbose_size=f'{i * 2}MB')

    logger.info(highlight('Downloaded {} successfully', '3 packages'))

    # 6. Warnings and errors (always show level)
    logger.warning('API rate limit at 80%', current=80, limit=100)

    footer = dedent("""
        ============================================================
        Tips:
          - Run without flags for clean output
          - Add -v for verbose context (_verbose_ keys)
          - Add -vv for debug context (_debug_ keys)
        ============================================================
    """)
    sys.stdout.write(footer)


if __name__ == '__main__':
    main()
