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
            'Processing dataset',
            'records: 1000',
            'pkg[ruff-format]',
            'ruff format --line-length=80 .',
            'pkg[pytest]',
            'pytest tests/ -v',
            'Database query completed',
            'duration: 150ms',
            'rows_affected: 42',
            'python setup.py build',
            'Summary',
            'verbosity level: 0',
            should_not_contain=[
                '_verbose_source',
                'source:',
                'format:',
                '_debug_file_size',
                'file_size:',
                'query:',
                'connection:',
                'query_plan:',
            ],
            desc='base_context_shown,_verbose/debug_prefixes_filtered_at_level_0',
        ),
        level_1(
            'Processing dataset',
            'records: 1000',
            'source: data.csv',
            'format: CSV',
            'pkg[ruff-format]',
            'files_changed: 14',
            'pkg[pytest]',
            'tests_passed: 95',
            'tests_failed: 5',
            'Database query completed',
            'duration: 150ms',
            'query: SELECT * FROM users',
            'connection: localhost:5432',
            'verbosity level: 1',
            should_not_contain=[
                'file_size:',
                'encoding:',
                'config:',
                'query_plan:',
                'cache_hit:',
            ],
            desc='verbose_prefixes_visible,_debug_hidden_at_level_1',
        ),
        level_2(
            'Processing dataset',
            'records: 1000',
            'source: data.csv',
            'format: CSV',
            'file_size: 2.5MB',
            'encoding: utf-8',
            'pkg[ruff-format]',
            'files_changed: 14',
            'config: .ruff.toml',
            'pkg[pytest]',
            'tests_passed: 95',
            'tests_failed: 5',
            'duration: 5.2s',
            'Database query completed',
            'query: SELECT * FROM users',
            'connection: localhost:5432',
            'query_plan: Sequential Scan',
            'cache_hit: true',
            'verbosity level: 2',
            desc='all_prefixes_including_debug_visible_at_level_2',
        ),
    ],
    ids=lambda e: e.description,
)
def test_prefixes_output(
    run_example_prefixes: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_prefixes output at different verbosity levels."""
    result = run_example_prefixes(expectation.args)
    verify_output(result, expectation)
