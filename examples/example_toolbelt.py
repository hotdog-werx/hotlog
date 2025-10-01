"""
Example demonstrating toolbelt-style tool execution logging

This shows how to log command executions in the format:
    tb[tool-name] => command

Run with:
    python example_toolbelt.py
    python example_toolbelt.py -v
    python example_toolbelt.py -vv
"""

import sys
from hotlog import configure_logging, get_logger, ToolMatch

# Parse verbosity from command line
verbosity = 0
if "-vv" in sys.argv or "--debug" in sys.argv:
    verbosity = 2
elif "-v" in sys.argv or "--verbose" in sys.argv:
    verbosity = 1

# Configure logging with ToolMatch matcher
configure_logging(
    verbosity=verbosity,
    matchers=[ToolMatch(event="executing", prefix="tb")],
)
logger = get_logger(__name__)

print(f"\n=== Toolbelt Style Logging (verbosity level: {verbosity}) ===\n")

# Example 1: Simple tool execution
logger.info(
    "executing",
    command="uvx ruff@0.13.0 --config .codeguide/configs/ruff.toml format --line-length=80 .",
    tool="ruff-format-80",
)

# Example 2: Tool execution with verbose context
logger.info(
    "executing",
    command="uvx add-trailing-comma@3.2.0 --exit-zero-even-if-changed file1.py file2.py file3.py",
    tool="add-trailing-comma",
    _verbose_file_count="34",
)

# Example 3: Tool execution with debug context
logger.info(
    "executing",
    command="uvx ruff@0.13.0 --config .codeguide/configs/ruff.toml format --line-length=120 .",
    tool="ruff-format-120",
    _verbose_files_changed="14",
    _debug_config_path=".codeguide/configs/ruff.toml",
)

# Example 4: Tool execution with result
logger.info(
    "executing",
    command="uvx ruff@0.13.0 --config .codeguide/configs/ruff.toml check --fix --fix-only .",
    tool="ruff-check-fix",
    _verbose_fixes_applied="5",
    _debug_exit_code="0",
)

# Example 5: Final tool execution
logger.info(
    "executing",
    command="uvx ruff@0.13.0 --config .codeguide/configs/ruff.toml format .",
    tool="ruff-format",
    _verbose_result="34 files left unchanged",
)

print("\n=== Toolbelt example completed ===\n")
