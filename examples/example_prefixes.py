"""Comprehensive example showing prefix filtering and tool execution.

Demonstrates:
1. How _verbose_ and _debug_ prefixes work automatically
2. Tool execution pattern using ToolMatch
3. Customizing the tool prefix

Run with:
    python example_prefixes.py           # Level 0
    python example_prefixes.py -v        # Level 1 (verbose)
    python example_prefixes.py -vv       # Level 2 (debug)
"""

import argparse
import sys
from textwrap import dedent

from hotlog import ToolMatch, configure_logging, get_logger


def main() -> None:
    """Run the prefix filtering example."""
    parser = argparse.ArgumentParser(
        description='Prefix filtering examples using hotlog',
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

    # Configure with custom tool matcher
    configure_logging(
        verbosity=verbosity,
        matchers=[ToolMatch(event='executing', prefix='pkg')],
    )
    logger = get_logger(__name__)

    header = dedent(f"""
        === Prefix Filtering Demo (verbosity level: {verbosity}) ===
    """)
    sys.stdout.write(header)

    # Example 1: Basic prefix filtering
    logger.info(
        'Processing dataset',
        records=1000,  # Always shown
        _verbose_source='data.csv',  # Only at -v or -vv
        _verbose_format='CSV',  # Only at -v or -vv
        _debug_file_size='2.5MB',  # Only at -vv
        _debug_encoding='utf-8',  # Only at -vv
    )

    # Example 2: More examples
    logger.info(
        'Database query completed',
        duration='150ms',  # Always shown
        rows_affected=42,  # Always shown
        _verbose_query='SELECT * FROM users',  # Only at -v or -vv
        _verbose_connection='localhost:5432',  # Only at -v or -vv
        _debug_query_plan='Sequential Scan',  # Only at -vv
        _debug_cache_hit=True,  # Only at -vv
    )

    section_header = dedent("""
        === Tool Execution Pattern Demo ===
    """)
    sys.stdout.write(section_header)

    # Example 3: Tool execution - AUTOMATIC formatting
    # Just use event="executing", command="...", tool="..."
    logger.info(
        'executing',
        command='ruff format --line-length=80 .',
        tool='ruff-format',
        _verbose_files_changed=14,
        _debug_config='.ruff.toml',
    )

    # Example 4: Another tool execution
    logger.info(
        'executing',
        command='pytest tests/ -v',
        tool='pytest',
        _verbose_tests_passed=95,
        _verbose_tests_failed=5,
        _debug_duration='5.2s',
    )

    # Example 5: Tool execution without tool name (still works!)
    logger.info(
        'executing',
        command='python setup.py build',
        _verbose_output='Build successful',
    )

    if verbosity == 0:
        summary = dedent(f"""
            === Summary ===

            At level {verbosity}:
              - Only base context shown (no _verbose_ or _debug_)
              - Tool executions show: pkg[tool] => command

            Note: The 'pkg' prefix is customizable via matchers=[ToolMatch(prefix='...')]
        """)
    elif verbosity == 1:
        summary = dedent(f"""
            === Summary ===

            At level {verbosity}:
              - Base + _verbose_ context shown
              - Tool executions show: pkg[tool] => command
              - Plus verbose details

            Note: The 'pkg' prefix is customizable via matchers=[ToolMatch(prefix='...')]
        """)
    else:
        summary = dedent(f"""
            === Summary ===

            At level {verbosity}:
              - Base + _verbose_ + _debug_ context shown
              - Tool executions show: pkg[tool] => command
              - Plus all debug details

            Note: The 'pkg' prefix is customizable via matchers=[ToolMatch(prefix='...')]
        """)

    sys.stdout.write(summary)


if __name__ == '__main__':
    main()
