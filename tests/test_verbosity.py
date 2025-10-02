"""Tests for verbosity configuration helpers."""

import argparse

import pytest

from hotlog.verbosity import (
    add_verbosity_argument,
    get_verbosity_from_env,
    resolve_verbosity,
)


@pytest.mark.parametrize(
    ('args', 'expected_verbose'),
    [
        ([], 0),
        (['-v'], 1),
        (['-vv'], 2),
        (['-vvv'], 3),  # Not capped by add_verbosity_argument itself
        (['--verbose'], 1),
        (['--verbose', '--verbose'], 2),
    ],
)
def test_add_verbosity_argument(args: list[str], expected_verbose: int) -> None:
    """Test that add_verbosity_argument adds -v/--verbose flag correctly."""
    parser = argparse.ArgumentParser()
    add_verbosity_argument(parser)
    parsed = parser.parse_args(args)
    assert parsed.verbose == expected_verbose


@pytest.mark.parametrize(
    ('env_vars', 'expected_verbosity'),
    [
        # No environment variables
        ({}, 0),
        # HOTLOG_VERBOSITY takes precedence
        ({'HOTLOG_VERBOSITY': '0'}, 0),
        ({'HOTLOG_VERBOSITY': '1'}, 1),
        ({'HOTLOG_VERBOSITY': '2'}, 2),
        # HOTLOG_VERBOSITY clamped to 0-2
        ({'HOTLOG_VERBOSITY': '5'}, 2),
        ({'HOTLOG_VERBOSITY': '-1'}, 0),
        # Invalid HOTLOG_VERBOSITY falls through to CI detection
        ({'HOTLOG_VERBOSITY': 'invalid', 'CI': 'true'}, 1),
        # GitHub Actions debug modes
        ({'RUNNER_DEBUG': '1'}, 2),
        ({'ACTIONS_RUNNER_DEBUG': 'true'}, 2),
        # CI environments return 1
        ({'CI': 'true'}, 1),
        ({'GITHUB_ACTIONS': 'true'}, 1),
        ({'GITLAB_CI': 'true'}, 1),
        ({'CIRCLECI': 'true'}, 1),
        ({'TRAVIS': 'true'}, 1),
        ({'JENKINS_HOME': '/var/jenkins'}, 1),
        ({'BUILDKITE': 'true'}, 1),
        # HOTLOG_VERBOSITY overrides debug mode
        ({'HOTLOG_VERBOSITY': '0', 'RUNNER_DEBUG': '1'}, 0),
        # Debug mode overrides CI
        ({'RUNNER_DEBUG': '1', 'CI': 'true'}, 2),
    ],
)
def test_get_verbosity_from_env(
    monkeypatch: pytest.MonkeyPatch,
    env_vars: dict[str, str],
    expected_verbosity: int,
) -> None:
    """Test environment variable detection for verbosity levels."""
    # Clear all relevant env vars first
    all_vars = [
        'HOTLOG_VERBOSITY',
        'RUNNER_DEBUG',
        'ACTIONS_RUNNER_DEBUG',
        'CI',
        'GITHUB_ACTIONS',
        'GITLAB_CI',
        'CIRCLECI',
        'TRAVIS',
        'JENKINS_HOME',
        'BUILDKITE',
    ]
    for var in all_vars:
        monkeypatch.delenv(var, raising=False)

    # Set test environment variables
    for var, value in env_vars.items():
        monkeypatch.setenv(var, value)

    assert get_verbosity_from_env() == expected_verbosity


@pytest.mark.parametrize(
    ('cli_verbose', 'env_vars', 'expected_verbosity'),
    [
        # No args, no env
        (None, {}, 0),
        # CLI only
        (0, {}, 0),
        (1, {}, 1),
        (2, {}, 2),
        (5, {}, 2),  # CLI capped at 2
        # Env only
        (None, {'CI': 'true'}, 1),
        (None, {'RUNNER_DEBUG': '1'}, 2),
        # CLI overrides when higher
        (2, {'CI': 'true'}, 2),
        # Env overrides when higher
        (1, {'RUNNER_DEBUG': '1'}, 2),
        # Both at same level
        (1, {'CI': 'true'}, 1),
        # Args with no verbose attribute
        ('no_attr', {'CI': 'true'}, 1),
    ],
)
def test_resolve_verbosity(
    monkeypatch: pytest.MonkeyPatch,
    cli_verbose: int | None | str,
    env_vars: dict[str, str],
    expected_verbosity: int,
) -> None:
    """Test verbosity resolution from CLI args and environment."""
    # Clear env vars
    for var in [
        'HOTLOG_VERBOSITY',
        'CI',
        'RUNNER_DEBUG',
        'ACTIONS_RUNNER_DEBUG',
    ]:
        monkeypatch.delenv(var, raising=False)

    # Set test environment
    for var, value in env_vars.items():
        monkeypatch.setenv(var, value)

    # Create args namespace
    if cli_verbose == 'no_attr':
        args = argparse.Namespace(other_attr='value')
    elif cli_verbose is None:
        args = None
    else:
        args = argparse.Namespace(verbose=cli_verbose)

    assert resolve_verbosity(args) == expected_verbosity


def test_full_workflow_with_parser(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test complete workflow from parser setup to verbosity resolution."""
    # Clear environment
    for var in ['CI', 'RUNNER_DEBUG', 'HOTLOG_VERBOSITY']:
        monkeypatch.delenv(var, raising=False)

    parser = argparse.ArgumentParser()
    add_verbosity_argument(parser)
    args = parser.parse_args(['-vv'])
    verbosity = resolve_verbosity(args)

    assert verbosity == 2


def test_ci_auto_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CI is auto-detected when no CLI args provided."""
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')

    parser = argparse.ArgumentParser()
    add_verbosity_argument(parser)
    args = parser.parse_args([])  # No -v flags
    verbosity = resolve_verbosity(args)

    assert verbosity == 1


def test_cli_and_env_combined_takes_max(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that maximum of CLI and env is used."""
    monkeypatch.setenv('CI', 'true')  # Would give 1

    parser = argparse.ArgumentParser()
    add_verbosity_argument(parser)

    # CLI at same level
    args = parser.parse_args(['-v'])
    assert resolve_verbosity(args) == 1

    # CLI at higher level
    args = parser.parse_args(['-vv'])
    assert resolve_verbosity(args) == 2

    # Env at higher level
    monkeypatch.setenv('RUNNER_DEBUG', '1')  # Now env gives 2
    args = parser.parse_args(['-v'])
    assert resolve_verbosity(args) == 2
