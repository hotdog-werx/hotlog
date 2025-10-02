"""hotlog live logging example.

Demonstrates live updates that disappear at verbosity level 0,
but stay visible at higher levels.

Run with:
    python example_live.py           # Level 0: live updates disappear
    python example_live.py -v        # Level 1: messages stay visible
    python example_live.py -vv       # Level 2: all debug info stays visible
"""

import argparse
import os
import sys
import time
from textwrap import dedent

from hotlog import configure_logging, get_logger, live_logging


def _sleep(seconds: float) -> None:
    """Sleep for the given time, unless HOTLOG_NO_DELAY is set."""
    if os.environ.get('HOTLOG_NO_DELAY'):
        return
    time.sleep(seconds)


def main() -> None:
    """Run the live logging example."""
    parser = argparse.ArgumentParser(
        description='Live logging example using hotlog',
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

    # Configure logging
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    header = dedent(f"""
        === Running with verbosity level {verbosity} ===
    """)
    sys.stdout.write(header)

    # Example 1: Live logging for a long operation
    with live_logging('Downloading repository...') as live:
        _sleep(1)
        live.info('Connected to server', host='github.com')
        _sleep(1)
        live.info('Fetching metadata', _verbose_size='2.5MB')
        _sleep(1)

    logger.info('Download completed', total_files=42, _verbose_duration='3.2s')

    # Example 2: Multiple sequential live operations
    with live_logging('Extracting files...') as live:
        _sleep(0.5)
        live.info('Unpacking archive', _verbose_compression='gzip')
        _sleep(0.5)
        live.debug('Validating checksums', _debug_algorithm='sha256')
        _sleep(0.5)
        live.warning('Large file detected', _verbose_file_size='250MB')
        _sleep(0.5)

    logger.info('Extraction completed', extracted_files=42)

    # Example 3: Live logging with progress
    with live_logging('Installing dependencies...') as live:
        for i in range(1, 6):
            _sleep(0.3)
            if i == 3:
                # Simulate an error during installation
                live.error(
                    'Package installation failed',
                    package=f'package-{i}',
                    error='checksum mismatch',
                )
            else:
                live.info(
                    f'Installed package {i}/5',
                    _verbose_package=f'package-{i}',
                )

    logger.info('Installation completed with errors')

    footer = dedent("""
        === Example completed ===

        Notice how at level 0, the 'live' messages disappear,
        but at level 1 and 2, all messages stay visible.
    """)
    sys.stdout.write(footer)


if __name__ == '__main__':
    main()
