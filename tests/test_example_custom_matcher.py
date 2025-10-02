"""
Integration tests for example_custom_matcher.py

Tests custom log matchers:
- InstallMatch for package installations
- ErrorMatch for error codes
- ToolMatch for tool execution
- Default formatting fallback
"""

from tests.conftest import (
    ExampleRunner,
    assert_contains_all,
    assert_not_contains_any,
)


# =============================================================================
# Custom matcher tests
# =============================================================================

def test_custom_matcher_level_0_default(run_example_custom_matcher: ExampleRunner):
    """Level 0: Test all custom matchers work at default verbosity."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # Basic output structure
    assert_contains_all(
        output,
        [
            "Custom Matcher Example (verbosity level: 0)",
            "Custom matcher example completed",
        ],
        context="level 0 basic output",
    )

    # InstallMatch: Should format package installations with checkmark
    assert_contains_all(
        output,
        [
            "Installed requests (version 2.31.0)",
            "Installed structlog (version 25.4.0)",
        ],
        context="InstallMatch formatting",
    )

    # ErrorMatch: Should format errors with error code
    assert_contains_all(
        output,
        [
            "[E001]",
            "Failed to connect to database",
        ],
        context="ErrorMatch formatting",
    )

    # ToolMatch: Should format tool execution
    assert_contains_all(
        output,
        [
            "pkg[uv-install] =>",
            "uv pip install requests",
        ],
        context="ToolMatch formatting",
    )

    # Default formatting: Regular message
    assert "Build completed successfully" in output

    # Should NOT show verbose details at level 0
    assert_not_contains_any(
        output,
        [
            "size: 120 KB",
            "cache_hit: true",
            "host: localhost:5432",
        ],
        context="level 0 verbose filtering",
    )


def test_custom_matcher_level_1_verbose(run_example_custom_matcher: ExampleRunner):
    """Level 1: Test that verbose context is shown."""
    result = run_example_custom_matcher(["-v"])

    assert result.returncode == 0
    output = result.clean_output

    # Should show all the same matchers
    assert_contains_all(
        output,
        [
            "Custom Matcher Example (verbosity level: 1)",
            "Installed requests",
            "Installed structlog",
            "[E001]",
            "Failed to connect to database",
            "pkg[uv-install] =>",
            "uv pip install requests",
            "Build completed successfully",
        ],
        context="level 1 matchers present",
    )

    # Should NOW show verbose details
    assert_contains_all(
        output,
        [
            "size: 120 KB",
            "cache_hit: true",
            "host: localhost:5432",
        ],
        context="level 1 verbose context",
    )


def test_install_match_with_and_without_version(run_example_custom_matcher: ExampleRunner):
    """Test that InstallMatch handles both with and without version."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # First install has explicit version
    assert "Installed requests (version 2.31.0)" in output

    # Second install should show version even without explicit one
    assert "Installed structlog (version 25.4.0)" in output


def test_error_match_formatting(run_example_custom_matcher: ExampleRunner):
    """Test that ErrorMatch formats error codes correctly."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # Error should be formatted with code prefix
    assert "[E001]" in output
    assert "Failed to connect to database" in output

    # At level 0, should not show verbose host
    assert "localhost:5432" not in output


def test_tool_match_formatting(run_example_custom_matcher: ExampleRunner):
    """Test that ToolMatch formats tool execution correctly."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # Tool execution should show prefix[tool] => command format
    assert "pkg[uv-install] =>" in output
    assert "uv pip install requests" in output


def test_default_formatting_fallback(run_example_custom_matcher: ExampleRunner):
    """Test that messages not matching custom matchers use default formatting."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # Regular message should appear without special formatting
    assert "Build completed successfully" in output


def test_multiple_matchers_coexist(run_example_custom_matcher: ExampleRunner):
    """Test that multiple custom matchers can coexist and all work."""
    result = run_example_custom_matcher([])

    assert result.returncode == 0
    output = result.clean_output

    # All three custom matchers should work
    assert "Installed requests" in output  # InstallMatch
    assert "[E001]" in output  # ErrorMatch
    assert "pkg[uv-install] =>" in output  # ToolMatch
    assert "Build completed successfully" in output  # Default
