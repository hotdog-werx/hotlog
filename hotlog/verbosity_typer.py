"""Typer-specific verbosity configuration helpers.

This module assumes typer is available. For conditional imports,
use the main hotlog.verbosity module instead.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer

import typer
from typer.models import OptionInfo


def add_verbosity_option() -> OptionInfo:
    """Create a Typer option for verbosity.

    Returns a Typer Option that can be used as a parameter in Typer commands.
    The option accepts -v/--verbose flags that can be repeated.

    Returns:
        A Typer Option configured for verbosity.

    Example:
        >>> import typer
        >>> from hotlog.verbosity_typer import add_verbosity_option
        >>> app = typer.Typer()
        >>> @app.command()
        ... def my_command(verbose: int = add_verbosity_option()):
        ...     # verbose will be 0, 1, or 2
        ...     pass
    """
    return typer.Option(
        0,
        '-v',
        '--verbose',
        count=True,
        help='Increase verbosity (-v for verbose, -vv for debug)',
    )
