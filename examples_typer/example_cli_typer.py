"""Real-world CLI example using hotlog with Typer.

Simulates a package manager CLI with different operations and verbosity levels.

Run with:
    python example_cli_typer.py install package-name
    python example_cli_typer.py -v install package-name
    python example_cli_typer.py -vv install package-name
"""

import os
import sys
import time
from textwrap import dedent

import typer
from structlog.typing import FilteringBoundLogger

from hotlog import (
    configure_logging,
    get_logger,
    live_logging,
    resolve_verbosity,
)
from hotlog.verbosity_typer import add_verbosity_option


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


app = typer.Typer(
    help='Example package manager CLI using hotlog with Typer',
    epilog="""
Examples:
  python example_cli_typer.py install mypackage
  python example_cli_typer.py -v install mypackage
  python example_cli_typer.py -vv update mypackage
    """,
)


@app.command()
def install(
    package: str = typer.Argument(..., help='Package name to install'),
    verbose: int = add_verbosity_option(),  # type: ignore[assignment]
) -> None:
    """Install a package."""
    # Resolve verbosity from CLI args and environment (CI detection)
    verbosity = resolve_verbosity(verbose=verbose)
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    header = dedent(f"""
        === Package Manager (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    install_package(package, logger)

    footer = dedent("""
        === Operation completed ===
    """)
    sys.stdout.write(footer)


@app.command()
def update(
    package: str = typer.Argument(..., help='Package name to update'),
    verbose: int = add_verbosity_option(),  # type: ignore[assignment]
) -> None:
    """Update a package."""
    # Resolve verbosity from CLI args and environment (CI detection)
    verbosity = resolve_verbosity(verbose=verbose)
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    header = dedent(f"""
        === Package Manager (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    update_package(package, logger)

    footer = dedent("""
        === Operation completed ===
    """)
    sys.stdout.write(footer)


@app.command()
def remove(
    package: str = typer.Argument(..., help='Package name to remove'),
    verbose: int = add_verbosity_option(),  # type: ignore[assignment]
) -> None:
    """Remove a package."""
    # Resolve verbosity from CLI args and environment (CI detection)
    verbosity = resolve_verbosity(verbose=verbose)
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    header = dedent(f"""
        === Package Manager (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    msg = f'Removing {package}'
    logger.info(msg)
    _sleep(0.5)
    logger.info('Package removed successfully')

    footer = dedent("""
        === Operation completed ===
    """)
    sys.stdout.write(footer)


if __name__ == '__main__':
    app()
