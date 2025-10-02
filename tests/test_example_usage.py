"""Parametrized tests for example_usage.py"""

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
            'Starting example application',
            'app_version: 1.0.0',
            'Processing data',
            'records: 100',
            should_not_contain=[
                '_verbose_source',
                'source:',
                'memory_usage:',
                'cache_hits:',
            ],
            desc='basic messages without verbose context',
        ),
        level_0(
            'Rate limit approaching',
            'current_requests: 95',
            'limit: 100',
            should_not_contain=['Internal state dump', '_debug_connections'],
            desc='warnings shown, debug hidden at level 0',
        ),
        level_1(
            'Processing data',
            'source: database.db',
            'query: SELECT * FROM users',
            'Analyzing results',
            'processing_time: 0.5s',
            should_not_contain=[
                'memory_usage:',
                'cache_hits:',
                'Internal state dump',
            ],
            desc='verbose context visible, debug hidden at level 1',
        ),
        level_2(
            'Analyzing results',
            'processing_time: 0.5s',
            'memory_usage: 45MB',
            'cache_hits: 42',
            'Internal state dump',
            'connections: 5',
            'queue_size: 12',
            'thread_pool: active',
            desc='debug context and messages visible at level 2',
        ),
        level_0(
            'Example completed',
            'Operation completed successfully',
            'duration: 2.3s',
            'items_processed: 100',
            desc='completion messages shown',
        ),
    ],
    ids=lambda e: e.description,
)
def test_usage_output(
    run_example_usage: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_usage output at different verbosity levels."""
    result = run_example_usage(expectation.args)
    verify_output(result, expectation)
