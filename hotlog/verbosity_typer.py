"""Typer-specific verbosity configuration helpers.

This module assumes typer is available. For conditional imports,
use the main hotlog.verbosity module instead.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer

import typer

# Pre-configured Typer option for verbosity
verbosity_option = typer.Option(
    0,
    '-v',
    '--verbose',
    count=True,
    help='Increase verbosity (-v for verbose, -vv for debug)',
)
