"""
Pytest configuration and shared fixtures for hotlog tests.

Provides utilities for capturing and asserting CLI output without mocking.
"""

import os
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture


def strip_ansi(text: str) -> str:
    """Remove ANSI color codes and Rich formatting from text."""
    # Remove ANSI escape sequences
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    # Remove Rich markup tags like [bold], [/bold], [blue], etc.
    text = re.sub(r"\[/?[a-z#0-9 ]+\]", "", text)
    return text


class Result(BaseModel):
    """Result of running a CLI command or example."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        """Combined stdout and stderr for unified output checking."""
        return (self.stdout or "") + (self.stderr or "")

    @property
    def clean_output(self) -> str:
        """Output with ANSI codes stripped."""
        return strip_ansi(self.output)


@dataclass
class RunExampleContext:
    """Context for running an example script."""

    example_name: str
    main_func: Callable
    args: list[str]
    cwd: Path
    capsys: pytest.CaptureFixture
    mocker: MockerFixture


def _run_example(ctx: RunExampleContext) -> Result:
    """
    Execute an example's main function with captured output.

    This runs the actual code without mocking to stress test the library.
    """
    old_cwd = Path.cwd()
    old_argv = sys.argv.copy()
    old_env = os.environ.get("HOTLOG_NO_DELAY")

    try:
        # Set environment variable to skip time.sleep() in examples
        os.environ["HOTLOG_NO_DELAY"] = "1"
        
        os.chdir(ctx.cwd)
        sys.argv = [ctx.example_name, *ctx.args]

        try:
            exit_code = ctx.main_func()
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 1
        else:
            exit_code = exit_code if exit_code is not None else 0

        captured = ctx.capsys.readouterr()
        stdout = captured.out
        stderr = captured.err

        return Result(
            returncode=exit_code,
            stdout=stdout,
            stderr=stderr,
        )
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv
        # Restore old environment variable
        if old_env is None:
            os.environ.pop("HOTLOG_NO_DELAY", None)
        else:
            os.environ["HOTLOG_NO_DELAY"] = old_env


# Type alias for example runner functions
ExampleRunner = Callable[[list[str]], Result]


@pytest.fixture
def run_example_cli(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """
    Fixture to run example_cli.py with captured output.

    Usage:
        result = run_example_cli(["install", "mypackage"])
        assert "Dependencies resolved" in result.clean_output
    """
    from examples.example_cli import main

    def _run(args: list[str]) -> Result:
        ctx = RunExampleContext(
            example_name="example_cli.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_toolbelt(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """
    Fixture to run example_toolbelt.py with captured output.

    Usage:
        result = run_example_toolbelt(["-v"])
        assert "tb[ruff-format-80]" in result.clean_output
    """
    # Import will be dynamic since we need to handle different verbosity levels
    def _run(args: list[str]) -> Result:
        from examples.example_toolbelt import main

        ctx = RunExampleContext(
            example_name="example_toolbelt.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_custom_matcher(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_custom_matcher.py with captured output."""

    def _run(args: list[str]) -> Result:
        from examples.example_custom_matcher import main

        ctx = RunExampleContext(
            example_name="example_custom_matcher.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_highlight(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_highlight.py with captured output."""

    def _run(args: list[str] | None = None) -> Result:
        from examples.example_highlight import main

        ctx = RunExampleContext(
            example_name="example_highlight.py",
            main_func=main,
            args=args or [],
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_live(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_live.py with captured output."""

    def _run(args: list[str]) -> Result:
        from examples.example_live import main

        ctx = RunExampleContext(
            example_name="example_live.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_prefixes(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_prefixes.py with captured output."""

    def _run(args: list[str]) -> Result:
        from examples.example_prefixes import main

        ctx = RunExampleContext(
            example_name="example_prefixes.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_usage(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_usage.py with captured output."""

    def _run(args: list[str]) -> Result:
        from examples.example_usage import main

        ctx = RunExampleContext(
            example_name="example_usage.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


@pytest.fixture
def run_example_quickstart(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    tmp_path: Path,
) -> ExampleRunner:
    """Fixture to run example_quickstart.py with captured output."""

    def _run(args: list[str]) -> Result:
        from examples.example_quickstart import main

        ctx = RunExampleContext(
            example_name="example_quickstart.py",
            main_func=main,
            args=args,
            cwd=tmp_path,
            capsys=capsys,
            mocker=mocker,
        )
        return _run_example(ctx)

    return _run


# Helper assertion functions


def assert_contains_all(output: str, snippets: list[str], context: str = ""):
    """
    Assert that all snippets appear in the output.

    Args:
        output: The text to search in
        snippets: List of strings that must all be present
        context: Optional context description for error messages
    """
    missing = [s for s in snippets if s not in output]
    if missing:
        ctx = f" in {context}" if context else ""
        pytest.fail(
            f"Missing expected snippet(s){ctx}:\n"
            f"  Missing: {missing}\n\n"
            f"Actual output:\n{output}"
        )


def assert_not_contains_any(output: str, snippets: list[str], context: str = ""):
    """
    Assert that none of the snippets appear in the output.

    Args:
        output: The text to search in
        snippets: List of strings that must NOT be present
        context: Optional context description for error messages
    """
    found = [s for s in snippets if s in output]
    if found:
        ctx = f" in {context}" if context else ""
        pytest.fail(
            f"Found unexpected snippet(s){ctx}:\n"
            f"  Found: {found}\n\n"
            f"Actual output:\n{output}"
        )


def assert_output_matches_verbosity(
    output: str,
    level: int,
    always_present: list[str],
    verbose_only: list[str] | None = None,
    debug_only: list[str] | None = None,
):
    """
    Assert output matches expected verbosity level filtering.

    Args:
        output: The captured output to check
        level: Verbosity level (0, 1, or 2)
        always_present: Snippets that should appear at all levels
        verbose_only: Snippets that should only appear at level 1+
        debug_only: Snippets that should only appear at level 2
    """
    verbose_only = verbose_only or []
    debug_only = debug_only or []

    # Always present at all levels
    assert_contains_all(output, always_present, f"level {level} (always present)")

    if level >= 1:
        # Verbose content should be visible
        assert_contains_all(output, verbose_only, f"level {level} (verbose)")
    else:
        # Verbose content should NOT be visible
        assert_not_contains_any(output, verbose_only, f"level {level} (verbose hidden)")

    if level >= 2:
        # Debug content should be visible
        assert_contains_all(output, debug_only, f"level {level} (debug)")
    else:
        # Debug content should NOT be visible
        assert_not_contains_any(output, debug_only, f"level {level} (debug hidden)")
