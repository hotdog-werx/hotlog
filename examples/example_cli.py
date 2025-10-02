"""Real-world CLI example using hotlog.

Simulates a package manager CLI with different operations and verbosity levels.

Run with:
    python example_cli.py install package-name
    python example_cli.py -v install package-name
    python example_cli.py -vv install package-name
"""

import argparse
import os
import sys
import time
from textwrap import dedent

from structlog.typing import FilteringBoundLogger

from hotlog import configure_logging, get_logger, live_logging


# Helper to make sleep time configurable (useful for tests)
def _sleep(seconds: float) -> None:
    """Sleep for the specified seconds, or skip if HOTLOG_NO_DELAY is set."""
    if os.environ.get('HOTLOG_NO_DELAY'):
        return
    time.sleep(seconds)


def install_package(package_name: str, logger: FilteringBoundLogger) -> None:
    """Simulate installing a package with various logging levels."""
    # Step 1: Resolve dependencies (live)
    with live_logging(f'Resolving dependencies for {package_name}...') as live:
        _sleep(0.8)
        live.info(
            'Dependency resolution started',
            package=package_name,
            _verbose_resolver='pip-compatible',
            _debug_cache_dir='~/.cache/hotlog',
        )
        _sleep(0.5)
        live.info(
            'Found dependencies',
            count=3,
            _verbose_deps='requests, pyyaml, click',
        )

    logger.info('Dependencies resolved', total=3, conflicts=0)

    # Step 2: Download packages (live)
    packages = [package_name, 'requests', 'pyyaml', 'click']
    with live_logging(f'Downloading {len(packages)} packages...') as live:
        for i, pkg in enumerate(packages, 1):
            _sleep(0.4)
            live.info(
                f'Downloaded {pkg}',
                progress=f'{i}/{len(packages)}',
                _verbose_size=f'{2.5 * i}MB',
                _debug_url=f'https://pypi.org/simple/{pkg}/',
            )

    logger.info(
        'Download completed',
        total_size='10.0MB',
        _verbose_duration='1.6s',
    )

    # Step 3: Install packages
    with live_logging('Installing packages...') as live:
        for pkg in packages:
            _sleep(0.3)
            live.info(
                f'Installing {pkg}',
                _verbose_location='/usr/local/lib/python3.11/site-packages',
                _debug_compile_bytecode=True,
            )

    logger.info(
        'Installation completed successfully',
        packages_installed=len(packages),
    )


def update_package(package_name: str, logger: FilteringBoundLogger) -> None:
    """Simulate updating a package."""
    logger.info('Checking for updates to %s', package_name)
    _sleep(0.5)

    logger.info(
        'Update available',
        current_version='1.0.0',
        new_version='1.2.0',
        _verbose_changelog_url='https://github.com/example/package/releases',
    )

    with live_logging(f'Updating {package_name}...') as live:
        _sleep(1)
        live.info('Downloading update', _verbose_size='3.5MB')
        _sleep(0.8)
        live.info('Applying update', _debug_backup_created=True)

    logger.info('Update completed', new_version='1.2.0')


def main() -> None:
    """Parse CLI arguments and execute the selected package command."""
    parser = argparse.ArgumentParser(
        description='Example package manager CLI using hotlog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s install mypackage
  %(prog)s -v install mypackage
  %(prog)s -vv update mypackage
        """,
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for verbose, -vv for debug)',
    )

    parser.add_argument(
        'command',
        choices=['install', 'update', 'remove'],
        help='Command to execute',
    )

    parser.add_argument('package', help='Package name')

    args = parser.parse_args()

    # Configure logging based on verbosity
    verbosity = min(args.verbose, 2)
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    header = dedent(f"""
        === Package Manager (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    if args.command == 'install':
        install_package(args.package, logger)
    elif args.command == 'update':
        update_package(args.package, logger)
    elif args.command == 'remove':
        msg = f'Removing {args.package}'
        logger.info(msg)
        _sleep(0.5)
        logger.info('Package removed successfully')

    footer = dedent("""
        === Operation completed ===
    """)
    sys.stdout.write(footer)


if __name__ == '__main__':
    main()
