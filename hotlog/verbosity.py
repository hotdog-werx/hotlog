"""Verbosity configuration helpers for CLI and CI environments."""

import argparse
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser


def add_verbosity_argument(parser: 'ArgumentParser') -> None:
    """Add standard verbosity argument to an argparse parser.

    Adds `-v/--verbose` flag that can be repeated for increased verbosity:
    - (no flag): verbosity level 0 (default, essential info only)
    - `-v`: verbosity level 1 (verbose, more context)
    - `-vv`: verbosity level 2 (debug, all information)

    Args:
        parser: The argparse ArgumentParser to add the verbosity argument to.

    Example:
        >>> import argparse
        >>> from hotlog import add_verbosity_argument, resolve_verbosity
        >>> parser = argparse.ArgumentParser()
        >>> add_verbosity_argument(parser)
        >>> args = parser.parse_args(['-vv'])
        >>> verbosity = resolve_verbosity(args)
        >>> print(verbosity)
        2
    """
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for verbose, -vv for debug)',
    )


def get_verbosity_from_env() -> int:
    """Detect verbosity level from CI/debug environment variables.

    Checks the following environment variables in order:
    1. HOTLOG_VERBOSITY: Explicit verbosity override (0, 1, or 2)
    2. RUNNER_DEBUG or ACTIONS_RUNNER_DEBUG: GitHub Actions debug mode → level 2
    3. CI, GITHUB_ACTIONS, GITLAB_CI, CIRCLECI, etc.: CI environment → level 1
    4. Default: level 0

    Returns:
        Detected verbosity level (0, 1, or 2)

    Example:
        >>> import os
        >>> os.environ['CI'] = 'true'
        >>> get_verbosity_from_env()
        1
        >>> os.environ['RUNNER_DEBUG'] = '1'
        >>> get_verbosity_from_env()
        2
    """
    # Explicit override
    if hotlog_verbosity := os.environ.get('HOTLOG_VERBOSITY'):
        try:
            return max(0, min(2, int(hotlog_verbosity)))
        except ValueError:
            pass

    # GitHub Actions debug mode
    if os.environ.get('RUNNER_DEBUG') == '1' or os.environ.get('ACTIONS_RUNNER_DEBUG') == 'true':
        return 2

    # CI environment detection (various CI platforms)
    ci_vars = [
        'CI',
        'GITHUB_ACTIONS',
        'GITLAB_CI',
        'CIRCLECI',
        'TRAVIS',
        'JENKINS_HOME',
        'BUILDKITE',
    ]
    if any(os.environ.get(var) for var in ci_vars):
        return 1

    # Default: no verbosity
    return 0


def resolve_verbosity(args: argparse.Namespace | None = None) -> int:
    """Resolve final verbosity level from CLI args and environment.

    CLI arguments take precedence over environment variables. If both are present,
    the higher verbosity level is used.

    Args:
        args: Parsed argparse Namespace with optional 'verbose' attribute.
              If None or missing 'verbose', only environment is checked.

    Returns:
        Final verbosity level (0, 1, or 2)

    Example:
        >>> import argparse
        >>> args = argparse.Namespace(verbose=1)
        >>> resolve_verbosity(args)  # Returns 1 or higher if CI detected
        1
    """
    env_verbosity = get_verbosity_from_env()
    cli_verbosity = 0

    if args and hasattr(args, 'verbose'):
        # Cap at level 2
        cli_verbosity = min(args.verbose, 2)

    # Take the maximum of both sources
    return max(env_verbosity, cli_verbosity)
