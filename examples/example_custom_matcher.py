"""Example demonstrating how to create a custom log matcher.

This shows how to extend the LogMatcher base class to create
custom formatting rules for specific log patterns.

Run with:
    python example_custom_matcher.py
    python example_custom_matcher.py -v
"""

import argparse
import sys
from textwrap import dedent

from structlog.typing import EventDict

from hotlog import LogMatcher, ToolMatch, configure_logging, get_logger


class InstallMatch(LogMatcher):
    """Custom matcher for package installation logs.

    Formats logs like: ✓ Installed package-name (version 1.2.3)
    """

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        """Match installation events at INFO level with 'package' key.
        
        Args:
            level: Log level (e.g., "INFO")
            event: Event message
            event_dict: Event context dictionary
        
        Returns:
            True if this matcher should handle the message
        """
        return level == 'INFO' and event == 'installed' and 'package' in event_dict

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> str | None:
        """Format as: ✓ Installed package-name (version 1.2.3).
        
        Args:
            level: Log level
            event: Event message
            event_dict: Event context dictionary (will be modified)

        Returns:
            Formatted message string, or None to use default formatting
        """
        package = event_dict.pop('package')
        version = event_dict.pop('version', 'unknown')

        return f'[green]✓[/green] Installed [bold]{package}[/bold] [dim](version {version})[/dim]'


class ErrorMatch(LogMatcher):
    """Custom matcher for error logs with error codes.

    Formats logs like: ✗ [E001] Error description
    """

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        """Match error events at ERROR level with 'error_code' key.
        
        Args:
            level: Log level (e.g., "ERROR")
            event: Event message
            event_dict: Event context dictionary
        
        Returns:
            True if this matcher should handle the message
        """
        return level == 'ERROR' and 'error_code' in event_dict

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> str | None:
        error_code = event_dict.pop('error_code')

        return f'[red]✗ [{error_code}][/red] [bold red]{event}[/bold red]'


def main() -> None:
    """Run the custom matcher example."""
    parser = argparse.ArgumentParser(
        description='Custom matcher example using hotlog',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity',
    )
    args = parser.parse_args()

    verbosity = args.verbose

    # Configure logging with multiple custom matchers
    configure_logging(
        verbosity=verbosity,
        matchers=[
            InstallMatch(),
            ErrorMatch(),
            ToolMatch(event='executing', prefix='pkg'),
        ],
    )
    logger = get_logger(__name__)

    header = dedent(f"""
        === Custom Matcher Example (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    # Example 1: Package installation (matched by InstallMatch)
    logger.info(
        'installed',
        package='requests',
        version='2.31.0',
        _verbose_size='120 KB',
    )

    logger.info(
        'installed',
        package='structlog',
        version='25.4.0',
    )

    # Example 2: Error with code (matched by ErrorMatch)
    logger.error(
        'Failed to connect to database',
        error_code='E001',
        _verbose_host='localhost:5432',
    )

    # Example 3: Tool execution (matched by ToolMatch)
    logger.info(
        'executing',
        command='uv pip install requests',
        tool='uv-install',
        _verbose_cache_hit=True,
    )

    # Example 4: Regular message (uses default formatting)
    logger.info('Build completed successfully')

    footer = dedent("""
        === Custom matcher example completed ===
    """)
    sys.stdout.write(footer)


if __name__ == '__main__':
    main()
