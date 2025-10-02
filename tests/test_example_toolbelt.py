"""
Integration tests for example_toolbelt.py

Tests ToolMatch formatting for tool execution logs:
- tb[tool-name] => command format
- Verbosity level filtering
- Tool execution with various context levels
"""

from tests.conftest import (
    ExampleRunner,
    assert_contains_all,
    assert_not_contains_any,
    assert_output_matches_verbosity,
)


# =============================================================================
# Toolbelt example tests
# =============================================================================

def test_toolbelt_level_0_default(run_example_toolbelt: ExampleRunner):
    """Level 0: Test basic tool execution logging."""
    result = run_example_toolbelt([])

    assert result.returncode == 0
    output = result.clean_output

    # Basic output structure
    assert_contains_all(
        output,
        [
            "Toolbelt Style Logging (verbosity level: 0)",
            "Toolbelt example completed",
        ],
        context="level 0 basic output",
    )

    # All tool executions should show with tb[tool] => command format
    assert_contains_all(
        output,
        [
            "tb[ruff-format-80] =>",
            "uvx ruff@0.13.0",
            "format --line-length=80",
            "tb[add-trailing-comma] =>",
            "uvx add-trailing-comma@3.2.0",
            "tb[ruff-format-120] =>",
            "format --line-length=120",
            "tb[ruff-check-fix] =>",
            "check --fix --fix-only",
            "tb[ruff-format] =>",
        ],
        context="ToolMatch formatting",
    )

    # Should NOT show verbose details at level 0
    assert_not_contains_any(
        output,
        [
            "file_count: 34",
            "files_changed: 14",
            "fixes_applied: 5",
            "result: 34 files left unchanged",
        ],
        context="level 0 verbose filtering",
    )

    # Should NOT show debug details at level 0
    assert_not_contains_any(
        output,
        [
            "config_path: .codeguide/configs/ruff.toml",
            "exit_code: 0",
        ],
        context="level 0 debug filtering",
    )


def test_toolbelt_level_1_verbose(run_example_toolbelt: ExampleRunner):
    """Level 1: Test that verbose context is shown."""
    result = run_example_toolbelt(["-v"])

    assert result.returncode == 0
    output = result.clean_output

    assert_output_matches_verbosity(
        output,
        level=1,
        always_present=[
            "Toolbelt Style Logging (verbosity level: 1)",
            "tb[ruff-format-80] =>",
            "tb[add-trailing-comma] =>",
            "tb[ruff-format-120] =>",
            "tb[ruff-check-fix] =>",
            "tb[ruff-format] =>",
        ],
        verbose_only=[
            "file_count:",
            "files_changed:",
            "fixes_applied:",
            "result: 34 files left unchanged",
        ],
        debug_only=[
            "config_path:",
            "exit_code:",
        ],
    )


def test_toolbelt_level_2_debug(run_example_toolbelt: ExampleRunner):
    """Level 2: Test that all context including debug is shown."""
    result = run_example_toolbelt(["-vv"])

    assert result.returncode == 0
    output = result.clean_output

    assert_output_matches_verbosity(
        output,
        level=2,
        always_present=[
            "Toolbelt Style Logging (verbosity level: 2)",
            "tb[ruff-format-80] =>",
            "tb[add-trailing-comma] =>",
        ],
        verbose_only=[
            "file_count:",
            "files_changed:",
            "fixes_applied:",
        ],
        debug_only=[
            "config_path:",
            "exit_code:",
        ],
    )


def test_toolbelt_tool_name_formatting(run_example_toolbelt: ExampleRunner):
    """Test that tool names are formatted correctly in brackets."""
    result = run_example_toolbelt([])

    assert result.returncode == 0
    output = result.clean_output

    # Each tool should have [tool-name] format
    assert "tb[ruff-format-80] =>" in output
    assert "tb[add-trailing-comma] =>" in output
    assert "tb[ruff-format-120] =>" in output
    assert "tb[ruff-check-fix] =>" in output
    assert "tb[ruff-format] =>" in output


def test_toolbelt_command_display(run_example_toolbelt: ExampleRunner):
    """Test that full commands are displayed."""
    result = run_example_toolbelt([])

    assert result.returncode == 0
    output = result.clean_output

    # Commands should be visible
    assert "uvx ruff@0.13.0" in output
    assert "uvx add-trailing-comma@3.2.0" in output
    assert "--config .codeguide/configs/ruff.toml" in output
    assert "--exit-zero-even-if-changed" in output


def test_toolbelt_multiple_tools_same_base(run_example_toolbelt: ExampleRunner):
    """Test that multiple executions of the same base tool are logged separately."""
    result = run_example_toolbelt([])

    assert result.returncode == 0
    output = result.clean_output

    # Multiple ruff invocations with different tool names
    assert "tb[ruff-format-80] =>" in output
    assert "tb[ruff-format-120] =>" in output
    assert "tb[ruff-check-fix] =>" in output
    assert "tb[ruff-format] =>" in output
