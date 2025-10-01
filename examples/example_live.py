"""
hotlog live logging example

Demonstrates live updates that disappear at verbosity level 0,
but stay visible at higher levels.

Run with:
    python example_live.py           # Level 0: live updates disappear
    python example_live.py -v        # Level 1: messages stay visible
    python example_live.py -vv       # Level 2: all debug info stays visible
"""

import sys
import time
from hotlog import configure_logging, get_logger, live_logging

# Parse verbosity from command line
verbosity = 0
if "-vv" in sys.argv or "--debug" in sys.argv:
    verbosity = 2
elif "-v" in sys.argv or "--verbose" in sys.argv:
    verbosity = 1

# Configure logging
configure_logging(verbosity=verbosity)
logger = get_logger(__name__)

print(f"\n=== Running with verbosity level {verbosity} ===\n")

# Example 1: Live logging for a long operation
with live_logging("Downloading repository...") as live:
    time.sleep(1)
    live.info("Connected to server", host="github.com")
    time.sleep(1)
    live.info("Fetching metadata", _verbose_size="2.5MB")
    time.sleep(1)

logger.info("Download completed", total_files=42, _verbose_duration="3.2s")

# Example 2: Multiple sequential live operations
with live_logging("Extracting files...") as live:
    time.sleep(0.5)
    live.info("Unpacking archive", _verbose_compression="gzip")
    time.sleep(0.5)
    live.info("Validating checksums", _debug_algorithm="sha256")
    time.sleep(0.5)

logger.info("Extraction completed", extracted_files=42)

# Example 3: Live logging with progress
with live_logging("Installing dependencies...") as live:
    for i in range(1, 6):
        time.sleep(0.3)
        live.info(f"Installed package {i}/5", _verbose_package=f"package-{i}")

logger.info("Installation completed successfully")

print("\n=== Example completed ===")
print("\nNotice how at level 0, the 'live' messages disappear,")
print("but at level 1 and 2, all messages stay visible.")
