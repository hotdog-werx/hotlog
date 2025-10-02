import pytest

from tests.conftest import ExampleRunner
from tests.test_helpers import CommandTest


@pytest.mark.parametrize(
    'test_case',
    [
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
            description='install_at_level_0',
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
            description='install_at_level_1_(verbose)',
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
            description='install_at_level_2_(debug)',
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
            description='update_at_level_0',
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
            description='update_at_level_1',
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
            description='update_at_level_2',
        ),
        # Remove command
        CommandTest(
            command=['remove', 'oldpackage'],
            verbosity=0,
            should_contain=[
                'Removing oldpackage',
                'Package removed successfully',
            ],
            description='remove_command',
        ),
        # Different package names
        CommandTest(
            command=['install', 'flask'],
            verbosity=0,
            should_contain=['Installation completed successfully'],
            description='install_flask',
        ),
        CommandTest(
            command=['install', 'django'],
            verbosity=0,
            should_contain=['Installation completed successfully'],
            description='install_django',
        ),
        # YAML formatting check
        CommandTest(
            command=['install', 'test-pkg'],
            verbosity=1,
            should_contain=[
                'resolver: pip-compatible',
                'location: /usr/local/lib/python3.11/site-packages',
            ],
            description='YAML_context_formatting',
        ),
        # Missing arguments - check stderr instead of stdout
        CommandTest(
            command=[],
            verbosity=0,
            should_contain=['usage:', 'install', 'update', 'remove'],
            should_fail=True,
            description='missing_arguments_shows_help',
        ),
        # Verbosity capping
        CommandTest(
            command=['install', 'pkg'],
            verbosity=2,
            should_contain=['Installation completed successfully'],
            description='verbosity_capped_at_2',
        ),
    ],
    ids=lambda t: t.description,
)
def test_cli_command(run_example_cli: ExampleRunner, test_case: CommandTest):
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
