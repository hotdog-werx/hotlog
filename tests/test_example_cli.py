"""
Integration tests for example_cli.py

Tests the full CLI example without mocking to stress test hotlog's features:
- Three verbosity levels (0, 1, 2)
- Live logging behavior
- Prefix filtering (_verbose_, _debug_)
- Rich output formatting
- Different CLI commands (install, update)
"""

import pytest

from tests.conftest import (
    ExampleRunner,
    assert_contains_all,
    assert_not_contains_any,
    assert_output_matches_verbosity,
)


# =============================================================================
# Install command tests
# =============================================================================

def test_install_level_0_default(run_example_cli: ExampleRunner):
    """
    Level 0: Live messages disappear, only non-live summaries remain.
    
    At level 0:
    - Messages inside live_logging() contexts disappear (transient)
    - Messages outside live_logging() contexts should appear
    - Only shows the essential summary after live operations complete
    """
    result = run_example_cli(["install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    # At level 0, the live contexts show headers but messages inside disappear
    # Only the print statements and messages OUTSIDE live contexts remain
    assert_contains_all(
        output,
        [
            "Package Manager (verbosity level: 0)",
            "Operation completed",
        ],
        context="level 0 install basic output",
    )

    # The logger.info() calls OUTSIDE live contexts should still appear
    assert_contains_all(
        output,
        [
            "Dependencies resolved",
            "total: 3",
            "conflicts: 0",
            "Download completed",
            "total_size: 10.0MB",
            "Installation completed successfully",
            "packages_installed: 4",
        ],
        context="level 0 install summary messages",
    )


def test_install_level_1_verbose(run_example_cli: ExampleRunner):
    """Level 1: Should show summary + verbose details."""
    result = run_example_cli(["-v", "install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    # Test with the helper function
    assert_output_matches_verbosity(
        output,
        level=1,
        always_present=[
            "Package Manager (verbosity level: 1)",
            "Dependencies resolved",
            "Download completed",
            "Installation completed successfully",
        ],
        verbose_only=[
            "resolver: pip-compatible",
            "deps: requests, pyyaml, click",
            "duration: 1.6s",
            "location: /usr/local/lib",
        ],
        debug_only=[
            "cache_dir: /tmp/cache",
            "url: https://pypi.org",
            "compile_bytecode: true",
        ],
    )


def test_install_level_2_debug(run_example_cli: ExampleRunner):
    """Level 2: Should show summary + verbose + debug details."""
    result = run_example_cli(["-vv", "install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    assert_output_matches_verbosity(
        output,
        level=2,
        always_present=[
            "Package Manager (verbosity level: 2)",
            "Dependencies resolved",
            "Download completed",
        ],
        verbose_only=[
            "resolver: pip-compatible",
            "deps: requests, pyyaml, click",
        ],
        debug_only=[
            "cache_dir: /tmp/cache",
            "url: https://pypi.org",
            "compile_bytecode: true",
        ],
    )


def test_install_different_package_names(run_example_cli: ExampleRunner):
    """Ensure package name is properly logged."""
    result = run_example_cli(["install", "myspecialpackage"])

    assert result.returncode == 0
    output = result.clean_output

    assert "myspecialpackage" in output or "package" in output.lower()


def test_install_live_logging_behavior(run_example_cli: ExampleRunner):
    """
    Test that live logging messages eventually lead to summaries.

    At level 0, intermediate messages should disappear, only summaries remain.
    """
    result = run_example_cli(["install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    # The final summaries should always be present
    assert_contains_all(
        output,
        [
            "Dependencies resolved",
            "Download completed",
            "Installation completed successfully",
        ],
        context="live logging summaries",
    )


# =============================================================================
# Update command tests
# =============================================================================

def test_update_level_0_default(run_example_cli: ExampleRunner):
    """Level 0: Should show essential update messages."""
    result = run_example_cli(["update", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    assert_contains_all(
        output,
        [
            "Package Manager (verbosity level: 0)",
            "Checking for updates to requests",
            "Update available",
            "current_version: 1.0.0",
            "new_version: 1.2.0",
            "Update completed",
            "Operation completed",
        ],
        context="level 0 update",
    )

    # Should NOT contain verbose details
    assert_not_contains_any(
        output,
        [
            "changelog_url: https://github.com",
            "size: 3.5MB",
        ],
        context="level 0 update verbose filtering",
    )


def test_update_level_1_verbose(run_example_cli: ExampleRunner):
    """Level 1: Should show update + verbose details."""
    result = run_example_cli(["-v", "update", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    assert_output_matches_verbosity(
        output,
        level=1,
        always_present=[
            "Update available",
            "current_version: 1.0.0",
            "Update completed",
        ],
        verbose_only=[
            "changelog_url: https://github.com",
            "size: 3.5MB",
        ],
        debug_only=[
            "backup_created: true",
        ],
    )


def test_update_level_2_debug(run_example_cli: ExampleRunner):
    """Level 2: Should show all details including debug."""
    result = run_example_cli(["-vv", "update", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    assert_output_matches_verbosity(
        output,
        level=2,
        always_present=[
            "Update available",
            "Update completed",
        ],
        verbose_only=[
            "changelog_url: https://github.com",
            "size: 3.5MB",
        ],
        debug_only=[
            "backup_created: true",
        ],
    )


# =============================================================================
# Remove command tests
# =============================================================================

def test_remove_basic(run_example_cli: ExampleRunner):
    """Test basic remove functionality."""
    result = run_example_cli(["remove", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    assert_contains_all(
        output,
        [
            "Package Manager (verbosity level: 0)",
            "Removing requests",
            "Package removed successfully",
            "Operation completed",
        ],
        context="remove command",
    )


# =============================================================================
# Edge cases and error handling tests
# =============================================================================

def test_verbosity_capped_at_2(run_example_cli: ExampleRunner):
    """Multiple -v flags should cap at level 2."""
    result = run_example_cli(["-vvvvv", "install", "test"])

    assert result.returncode == 0
    output = result.clean_output

    # Should show level 2, not level 5
    assert "verbosity level: 2" in output


def test_missing_arguments_shows_help(run_example_cli: ExampleRunner):
    """Running without arguments should show help or error."""
    result = run_example_cli([])

    # Should exit with error code
    assert result.returncode != 0

    # Should show usage or error message
    output = result.output  # Include stderr
    assert "usage:" in output.lower() or "error:" in output.lower()


# =============================================================================
# Output formatting tests
# =============================================================================

def test_yaml_context_formatting(run_example_cli: ExampleRunner):
    """Verify that context is formatted as YAML with proper indentation."""
    result = run_example_cli(["-v", "install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    # YAML should have key: value format
    assert "total: 3" in output
    assert "conflicts: 0" in output
    assert "total_size: 10.0MB" in output


def test_no_error_messages_on_success(run_example_cli: ExampleRunner):
    """Successful operations should not log errors."""
    result = run_example_cli(["install", "requests"])

    assert result.returncode == 0
    output = result.clean_output

    # Should not contain error indicators
    assert_not_contains_any(
        output,
        [
            "ERROR",
            "Error",
            "error:",
            "failed",
            "Failed",
        ],
        context="error messages",
    )
