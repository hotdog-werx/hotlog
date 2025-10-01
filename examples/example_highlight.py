"""
Example showing how to highlight important information in messages

Demonstrates:
1. Direct Rich markup in messages
2. Using the highlight() helper
3. Event-based messages with highlighted context summaries

Run with:
    python example_highlight.py
    python example_highlight.py -v
"""

import sys
from hotlog import configure_logging, get_logger, highlight

# Parse verbosity from command line
verbosity = 0
if "-v" in sys.argv:
    verbosity = 1

# Configure logging
configure_logging(verbosity=verbosity)
logger = get_logger(__name__)

print(f"\n=== Highlighting Examples (verbosity level: {verbosity}) ===\n")

# Example 1: Direct Rich markup (simplest)
logger.info("Installed [bold]5 packages[/bold] in [bold]3ms[/bold]")

# Example 2: Using the highlight() helper
logger.info(highlight("Downloaded {} in {}", "14 files", "2.5s"))

# Example 3: Event-based message with highlighted summary (level 0 only)
# This is perfect for level 0 where you want a clean summary
logger.info(
    highlight(
        "Resolved {} with {} in {}",
        "42 dependencies",
        "no conflicts",
        "150ms",
    ),
    _verbose_packages="react, vue, angular, ...",
    _verbose_registry="https://registry.npmjs.org",
)

# Example 4: Mixed - some bold, some not
logger.info("Processing [bold]100 records[/bold] from database")

# Example 5: Event name with highlighted values
logger.info(
    highlight(
        "Compilation completed: {} successful, {} failed",
        "95 files",
        "5 files",
    ),
    _verbose_duration="5.2s",
    _verbose_warnings="12",
)

# Example 6: Numbers and units
logger.info(highlight("Cache size: {} ({})", "2.5GB", "1,234 entries"))

# Example 7: With warning
logger.warning(
    highlight(
        "Rate limit approaching: {} of {} used",
        "95 requests",
        "100 requests",
    ),
)

print("\n=== Examples completed ===")
print("\nNotice how at level 0, only the summary message appears.")
print("At level 1 (-v), you also see the verbose context.")
