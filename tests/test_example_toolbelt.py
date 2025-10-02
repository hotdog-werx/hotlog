"""Parametrized tests for example_toolbelt.py"""

import pytest

from tests.conftest import ExampleRunner
from tests.test_helpers import (
    OutputExpectation,
    level_0,
    level_1,
    level_2,
    verify_output,
)


@pytest.mark.parametrize(
    'expectation',
    [
        level_0(
            'Toolbelt Style Logging (verbosity level: 0)',
            'tb[ruff-format-80] =>',
            'uvx ruff@0.13.0',
            'format --line-length=80',
            'tb[add-trailing-comma] =>',
            'uvx add-trailing-comma@3.2.0',
            'tb[ruff-format-120] =>',
            'format --line-length=120',
            'tb[ruff-check-fix] =>',
            'check --fix --fix-only',
            'tb[ruff-format] =>',
            'Toolbelt example completed',
            should_not_contain=[
                'file_count: 34',
                'files_changed: 14',
                'fixes_applied: 5',
                'config_path:',
                'exit_code:',
            ],
            desc='basic_tool_execution_logging_without_verbose/debug_details',
        ),
        level_1(
            'Toolbelt Style Logging (verbosity level: 1)',
            'tb[ruff-format-80] =>',
            'tb[add-trailing-comma] =>',
            'tb[ruff-format-120] =>',
            'tb[ruff-check-fix] =>',
            'tb[ruff-format] =>',
            'file_count:',
            'files_changed:',
            'fixes_applied:',
            'result: 34 files left unchanged',
            should_not_contain=['config_path:', 'exit_code:'],
            desc='verbose_context_visible,_debug_hidden',
        ),
        level_2(
            'Toolbelt Style Logging (verbosity level: 2)',
            'tb[ruff-format-80] =>',
            'tb[add-trailing-comma] =>',
            'file_count:',
            'files_changed:',
            'fixes_applied:',
            'config_path:',
            'exit_code:',
            desc='all_context_including_debug_visible',
        ),
        level_0(
            'tb[ruff-format-80] =>',
            'tb[add-trailing-comma] =>',
            'tb[ruff-format-120] =>',
            'tb[ruff-check-fix] =>',
            'tb[ruff-format] =>',
            'uvx ruff@0.13.0',
            'uvx add-trailing-comma@3.2.0',
            '--config .codeguide/configs/ruff.toml',
            '--exit-zero-even-if-changed',
            desc='tool_names_formatted_and_commands_displayed',
        ),
    ],
    ids=lambda e: e.description,
)
def test_toolbelt_output(
    run_example_toolbelt: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_toolbelt output at different verbosity levels."""
    result = run_example_toolbelt(expectation.args)
    verify_output(result, expectation)
