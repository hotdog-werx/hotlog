"""
hotlog example usage demonstrating three verbosity levels

Run with:
    python example_usage.py           # Level 0: default, minimal output
    python example_usage.py -v        # Level 1: verbose, more context
    python example_usage.py -vv       # Level 2: debug, all details
"""

import argparse
from hotlog import configure_logging, get_logger


def main():
    """Run the usage example."""
    parser = argparse.ArgumentParser(description="Usage examples with different verbosity levels")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for verbose, -vv for debug)",
    )
    args = parser.parse_args()

    verbosity = args.verbose

    # Configure logging with appropriate verbosity
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    print(f"\n=== Running with verbosity level {verbosity} ===\n")

    # Example 1: Basic logging
    logger.info("Starting example application", app_version="1.0.0")

    # Example 2: Log with verbose context (only shown in -v or -vv)
    logger.info(
        "Processing data",
        records=100,
        _verbose_source="database.db",
        _verbose_query="SELECT * FROM users",
    )

    # Example 3: Log with debug context (only shown in -vv)
    logger.info(
        "Analyzing results",
        total_records=100,
        _verbose_processing_time="0.5s",
        _debug_memory_usage="45MB",
        _debug_cache_hits=42,
    )

    # Example 4: Warning with context
    logger.warning("Rate limit approaching", current_requests=95, limit=100)

    # Example 5: Debug level message (only shown in -vv)
    logger.debug(
        "Internal state dump",
        _debug_connections=5,
        _debug_queue_size=12,
        _debug_thread_pool="active",
    )

    # Example 6: Success-style message
    logger.info(
        "Operation completed successfully",
        duration="2.3s",
        items_processed=100,
    )

    print("\n=== Example completed ===")
    print("\nTry running with different verbosity levels:")
    print("  python example_usage.py     # Default (level 0)")
    print("  python example_usage.py -v  # Verbose (level 1)")
    print("  python example_usage.py -vv # Debug (level 2)")


if __name__ == "__main__":
    main()
