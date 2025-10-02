"""Shared test utilities for parametrized example tests."""

from dataclasses import dataclass

from .conftest import Result


@dataclass
class CommandTest:
    """Define a CLI command test case with expectations.

    This is for examples that accept command-style arguments (like CLI tools)
    plus verbosity flags. The verbosity is specified as an integer and will
    be converted to the appropriate number of -v flags.

    Attributes:
        command: The command arguments (e.g., ["install", "mypackage"])
        verbosity: Verbosity level (0, 1, or 2)
        should_contain: List of strings that must appear in stdout (or stderr if should_fail=True)
        should_not_contain: List of strings that must NOT appear in stdout
        description: Human-readable description for test identification
        should_fail: Whether the command is expected to fail (default: False)
    """

    command: list[str]
    verbosity: int
    should_contain: list[str]
    should_not_contain: list[str] | None = None
    description: str = ''
    should_fail: bool = False

    def __post_init__(self) -> None:
        """Ensure should_not_contain is a list."""
        if self.should_not_contain is None:
            self.should_not_contain = []

    @property
    def args(self) -> list[str]:
        """Get full command line args including verbosity flags."""
        args = list(self.command)
        if self.verbosity == 1:
            args.append('-v')
        elif self.verbosity == 2:
            args.extend(['-v', '-v'])
        return args


@dataclass
class OutputExpectation:
    """Define expected output at a specific verbosity level.

    This is a generic expectation that works for any example.

    Attributes:
        args: Command line arguments (e.g., [], ["-v"], ["-v", "-v"])
        should_contain: List of strings that must appear in stdout
        should_not_contain: List of strings that must NOT appear in stdout
        description: Human-readable description for test identification
        should_fail: Whether the command is expected to fail (default: False)
    """

    args: list[str]
    should_contain: list[str]
    should_not_contain: list[str] | None = None
    description: str = ''
    should_fail: bool = False

    def __post_init__(self) -> None:
        """Ensure should_not_contain is a list."""
        if self.should_not_contain is None:
            self.should_not_contain = []

    @property
    def verbosity(self) -> int:
        """Infer verbosity level from args."""
        v_count = self.args.count('-v')
        return min(v_count, 2)  # Cap at 2


def verify_output(result: Result, expectation: OutputExpectation) -> None:
    """Verify that result matches expectation.

    Args:
        result: The result object from running an example
        expectation: The OutputExpectation to verify against

    Raises:
        AssertionError: If expectations are not met
    """
    # Check return code
    if not expectation.should_fail:
        assert result.returncode == 0, (
            f'Command failed unexpectedly:\nstdout: {result.stdout}\nstderr: {result.stderr}'
        )

    # Check all expected strings are present
    for expected in expectation.should_contain:
        assert expected in result.stdout, f"Expected '{expected}' not found in output.\nFull output:\n{result.stdout}"

    # Check all forbidden strings are absent
    if expectation.should_not_contain:
        for forbidden in expectation.should_not_contain:
            assert forbidden not in result.stdout, (
                f"Unexpected '{forbidden}' found in output.\nFull output:\n{result.stdout}"
            )


# Helper functions to create common expectations
def level_0(
    *should_contain: str,
    should_not_contain: list[str] | None = None,
    desc: str = '',
) -> OutputExpectation:
    """Create a level 0 (default) expectation."""
    return OutputExpectation(
        args=[],
        should_contain=list(should_contain),
        should_not_contain=should_not_contain,
        description=desc or 'level 0 (default)',
    )


def level_1(
    *should_contain: str,
    should_not_contain: list[str] | None = None,
    desc: str = '',
) -> OutputExpectation:
    """Create a level 1 (verbose) expectation."""
    return OutputExpectation(
        args=['-v'],
        should_contain=list(should_contain),
        should_not_contain=should_not_contain,
        description=desc or 'level 1 (verbose)',
    )


def level_2(
    *should_contain: str,
    should_not_contain: list[str] | None = None,
    desc: str = '',
) -> OutputExpectation:
    """Create a level 2 (debug) expectation."""
    return OutputExpectation(
        args=['-v', '-v'],
        should_contain=list(should_contain),
        should_not_contain=should_not_contain,
        description=desc or 'level 2 (debug)',
    )
