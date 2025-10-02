"""
Example demonstrating how to create a custom log matcher

This shows how to extend the LogMatcher base class to create
custom formatting rules for specific log patterns.

Run with:
    python example_custom_matcher.py
    python example_custom_matcher.py -v
"""

import argparse
from hotlog import configure_logging, get_logger, LogMatcher, ToolMatch
from structlog.typing import EventDict
from typing import Optional


class InstallMatch(LogMatcher):
    """Custom matcher for package installation logs.

    Formats logs like: ✓ Installed package-name (version 1.2.3)
    """

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        return level == "INFO" and event == "installed" and "package" in event_dict

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> Optional[str]:
        package = event_dict.pop("package")
        version = event_dict.pop("version", "unknown")

        return f"[green]✓[/green] Installed [bold]{package}[/bold] [dim](version {version})[/dim]"


class ErrorMatch(LogMatcher):
    """Custom matcher for error logs with error codes.

    Formats logs like: ✗ [E001] Error description
    """

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        return level == "ERROR" and "error_code" in event_dict

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> Optional[str]:
        error_code = event_dict.pop("error_code")

        return f"[red]✗ [{error_code}][/red] [bold red]{event}[/bold red]"


def main():
    """Run the custom matcher example."""
    parser = argparse.ArgumentParser(description="Custom matcher example using hotlog")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity",
    )
    args = parser.parse_args()

    verbosity = args.verbose

    # Configure logging with multiple custom matchers
    configure_logging(
        verbosity=verbosity,
        matchers=[
            InstallMatch(),
            ErrorMatch(),
            ToolMatch(event="executing", prefix="pkg"),
        ],
    )
    logger = get_logger(__name__)

    print(f"\n=== Custom Matcher Example (verbosity level: {verbosity}) ===\n")

    # Example 1: Package installation (matched by InstallMatch)
    logger.info(
        "installed",
        package="requests",
        version="2.31.0",
        _verbose_size="120 KB",
    )

    logger.info(
        "installed",
        package="structlog",
        version="25.4.0",
    )

    # Example 2: Error with code (matched by ErrorMatch)
    logger.error(
        "Failed to connect to database",
        error_code="E001",
        _verbose_host="localhost:5432",
    )

    # Example 3: Tool execution (matched by ToolMatch)
    logger.info(
        "executing",
        command="uv pip install requests",
        tool="uv-install",
        _verbose_cache_hit=True,
    )

    # Example 4: Regular message (uses default formatting)
    logger.info("Build completed successfully")

    print("\n=== Custom matcher example completed ===")


if __name__ == "__main__":
    main()

