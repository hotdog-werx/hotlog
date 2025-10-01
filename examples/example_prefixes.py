"""
Comprehensive example showing prefix filtering and tool execution

Demonstrates:
1. How _verbose_ and _debug_ prefixes work automatically
2. Tool execution pattern using ToolMatch
3. Customizing the tool prefix

Run with:
    python example_prefixes.py           # Level 0
    python example_prefixes.py -v        # Level 1 (verbose)
    python example_prefixes.py -vv       # Level 2 (debug)
"""

import sys
from hotlog import configure_logging, get_logger, ToolMatch

# Parse verbosity
verbosity = 0
if "-vv" in sys.argv:
    verbosity = 2
elif "-v" in sys.argv:
    verbosity = 1

# Configure with custom tool matcher
configure_logging(
    verbosity=verbosity,
    matchers=[ToolMatch(event="executing", prefix="pkg")],
)
logger = get_logger(__name__)

print(f"\n=== Prefix Filtering Demo (verbosity level: {verbosity}) ===\n")

# Example 1: Basic prefix filtering
logger.info(
    "Processing dataset",
    records=1000,  # Always shown
    _verbose_source="data.csv",  # Only at -v or -vv
    _verbose_format="CSV",  # Only at -v or -vv
    _debug_file_size="2.5MB",  # Only at -vv
    _debug_encoding="utf-8",  # Only at -vv
)

# Example 2: More examples
logger.info(
    "Database query completed",
    duration="150ms",  # Always shown
    rows_affected=42,  # Always shown
    _verbose_query="SELECT * FROM users",  # Only at -v or -vv
    _verbose_connection="localhost:5432",  # Only at -v or -vv
    _debug_query_plan="Sequential Scan",  # Only at -vv
    _debug_cache_hit=True,  # Only at -vv
)

print("\n=== Tool Execution Pattern Demo ===\n")

# Example 3: Tool execution - AUTOMATIC formatting
# Just use event="executing", command="...", tool="..."
logger.info(
    "executing",
    command="ruff format --line-length=80 .",
    tool="ruff-format",
    _verbose_files_changed=14,
    _debug_config=".ruff.toml",
)

# Example 4: Another tool execution
logger.info(
    "executing",
    command="pytest tests/ -v",
    tool="pytest",
    _verbose_tests_passed=95,
    _verbose_tests_failed=5,
    _debug_duration="5.2s",
)

# Example 5: Tool execution without tool name (still works!)
logger.info(
    "executing",
    command="python setup.py build",
    _verbose_output="Build successful",
)

print("\n=== Summary ===")
print(f"\nAt level {verbosity}:")
if verbosity == 0:
    print("  - Only base context shown (no _verbose_ or _debug_)")
    print("  - Tool executions show: pkg[tool] => command")
elif verbosity == 1:
    print("  - Base + _verbose_ context shown")
    print("  - Tool executions show: pkg[tool] => command")
    print("  - Plus verbose details")
else:
    print("  - Base + _verbose_ + _debug_ context shown")
    print("  - Tool executions show: pkg[tool] => command")
    print("  - Plus all debug details")

print(
    "\nNote: The 'pkg' prefix is customizable via matchers=[ToolMatch(prefix='...')]",
)
