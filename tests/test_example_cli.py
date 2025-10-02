"""Parametrized tests for example_cli.py"""

import pytest

from tests.test_helpers import CommandTest

# Test data for example_cli
CLI_EXPECTATIONS = [
    # Install command at different verbosity levels
    CommandTest(
        command=['install', 'mypackage'],
        verbosity=0,
        should_contain=[
            'Dependencies resolved',
            'total: 3',
            'Installation completed successfully',
        ],
        should_not_contain=[
            'resolver:',
            'location:',
            'compile_bytecode:',
            'url:',
        ],
        description='install at level 0',
    ),
    CommandTest(
        command=['install', 'mypackage'],
        verbosity=1,
        should_contain=[
            'Dependencies resolved',
            'Installing mypackage',
            'Installation completed successfully',
            'location: /usr/local/lib/python3.11/site-packages',
        ],
        should_not_contain=['compile_bytecode:', 'url:'],
        description='install at level 1 (verbose)',
    ),
    CommandTest(
        command=['install', 'mypackage'],
        verbosity=2,
        should_contain=[
            'Dependencies resolved',
            'Installing mypackage',
            'Installation completed successfully',
            'location: /usr/local/lib/python3.11/site-packages',
            'compile_bytecode: true',
            'url: https://pypi.org/simple/',
        ],
        description='install at level 2 (debug)',
    ),
    # Update command
    CommandTest(
        command=['update', 'requests'],
        verbosity=0,
        should_contain=[
            'Checking for updates',
            'Update completed',
        ],
        should_not_contain=['changelog_url:', 'backup_created:'],
        description='update at level 0',
    ),
    CommandTest(
        command=['update', 'requests'],
        verbosity=1,
        should_contain=[
            'Checking for updates',
            'Update completed',
            'current_version:',
            'new_version:',
        ],
        should_not_contain=['backup_created:'],
        description='update at level 1',
    ),
    CommandTest(
        command=['update', 'requests'],
        verbosity=2,
        should_contain=[
            'Checking for updates',
            'Update completed',
            'current_version:',
            'new_version:',
            'backup_created:',
        ],
        description='update at level 2',
    ),
    # Remove command
    CommandTest(
        command=['remove', 'oldpackage'],
        verbosity=0,
        should_contain=[
            'Removing oldpackage',
            'Package removed successfully',
        ],
        description='remove command',
    ),
    # Different package names
    CommandTest(
        command=['install', 'flask'],
        verbosity=0,
        should_contain=['Installation completed successfully'],
        description='install flask',
    ),
    CommandTest(
        command=['install', 'django'],
        verbosity=0,
        should_contain=['Installation completed successfully'],
        description='install django',
    ),
    # YAML formatting check
    CommandTest(
        command=['install', 'test-pkg'],
        verbosity=1,
        should_contain=[
            'resolver: pip-compatible',
            'location: /usr/local/lib/python3.11/site-packages',
        ],
        description='YAML context formatting',
    ),
    # Missing arguments - check stderr instead of stdout
    CommandTest(
        command=[],
        verbosity=0,
        should_contain=['usage:', 'install', 'update', 'remove'],
        should_fail=True,
        description='missing arguments shows help',
    ),
    # Verbosity capping
    CommandTest(
        command=['install', 'pkg'],
        verbosity=2,
        should_contain=['Installation completed successfully'],
        description='verbosity capped at 2',
    ),
]


@pytest.mark.parametrize(
    'test_case',
    CLI_EXPECTATIONS,
    ids=lambda t: t.description,
)
def test_cli_command(run_example_cli, test_case: CommandTest):
    """Test example_cli commands at different verbosity levels."""
    result = run_example_cli(test_case.args)

    # Check return code
    if not test_case.should_fail:
        assert result.returncode == 0, f'Command failed unexpectedly: {result.stderr}'

    # For help/error messages, check stderr; otherwise check stdout
    output = result.stderr if test_case.should_fail else result.stdout

    # Check all expected strings are present
    for expected in test_case.should_contain:
        assert expected in output, f"Expected '{expected}' not found in output"

    # Check all forbidden strings are absent
    if test_case.should_not_contain:
        for forbidden in test_case.should_not_contain:
            assert forbidden not in result.stdout, f"Unexpected '{forbidden}' found in output"

    # Ensure no error messages on success
    if not test_case.should_fail:
        assert 'ERROR' not in result.stdout
        assert 'FAILED' not in result.stdout
