"""Example demonstrating exception logging with hotlog.

This example shows how hotlog handles and displays exceptions,
including stack traces and context information.

Run with:
    python example_exceptions.py           # Level 0: default output
    python example_exceptions.py -v        # Level 1: verbose output
    python example_exceptions.py -vv       # Level 2: debug output
"""

import argparse
import sys

from pydantic import BaseModel, ValidationError

from hotlog import configure_logging, get_logger


class DatabaseConfig(BaseModel):
    """Example configuration model."""

    host: str
    port: int
    database: str
    username: str
    max_connections: int


def divide_numbers(a: int, b: int) -> float:
    """Divide two numbers.

    Args:
        a: The numerator
        b: The denominator

    Returns:
        The result of a / b

    Raises:
        ZeroDivisionError: If b is zero
    """
    return a / b


def process_data(data: dict[str, int]) -> int:
    """Process some data that may raise exceptions.

    Args:
        data: Dictionary with numeric values

    Returns:
        Sum of all values

    Raises:
        KeyError: If required key is missing
        TypeError: If values aren't numeric
    """
    result = data['required_field'] + data['other_field']
    return result


def nested_exception_example() -> None:
    """Demonstrate nested exception handling."""

    def inner_function() -> None:
        """Inner function that raises an exception."""
        msg = 'Something went wrong in the inner function'
        raise ValueError(msg)

    def middle_function() -> None:
        """Middle function that calls inner."""
        inner_function()

    def outer_function() -> None:
        """Outer function that starts the chain."""
        middle_function()

    outer_function()


def main() -> None:
    """Run the exception examples."""
    parser = argparse.ArgumentParser(
        description='Exception handling examples for hotlog',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for verbose, -vv for debug)',
    )
    args = parser.parse_args()

    verbosity = args.verbose

    # Configure logging with appropriate verbosity
    configure_logging(verbosity=verbosity)
    logger = get_logger(__name__)

    sys.stdout.write(f'\n=== Exception Logging Examples (verbosity level {verbosity}) ===\n\n')

    # Example 1: ZeroDivisionError
    logger.info('Example 1: Division by zero')
    try:
        result = divide_numbers(10, 0)
        logger.info('Division successful', result=result)
    except ZeroDivisionError as e:
        logger.error(
            'Division failed',
            error=str(e),
            numerator=10,
            denominator=0,
            exc_info=True,
        )

    # Example 2: KeyError with context
    logger.info('\nExample 2: Missing required field')
    try:
        data = {'other_field': 42}  # Missing 'required_field'
        result = process_data(data)
        logger.info('Processing successful', result=result)
    except KeyError as e:
        logger.error(
            'Data processing failed',
            error=str(e),
            provided_keys=list(data.keys()),
            _verbose_data=data,
            exc_info=True,
        )

    # Example 3: Nested exception with full stack trace
    logger.info('\nExample 3: Nested function exception')
    try:
        nested_exception_example()
    except ValueError as e:
        logger.error(
            'Nested operation failed',
            error=str(e),
            error_type=type(e).__name__,
            _debug_full_context='This shows the complete call stack',
            exc_info=True,
        )

    # Example 4: Custom exception with additional context
    logger.info('\nExample 4: Custom exception with rich context')
    try:
        config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'mydb',
            'user': 'admin',
        }
        # Simulate a connection error
        msg = 'Connection timeout after 30 seconds'
        raise ConnectionError(msg)
    except ConnectionError as e:
        logger.error(
            'Database connection failed',
            error=str(e),
            host=config['host'],
            port=config['port'],
            database=config['database'],
            _verbose_user=config['user'],
            _verbose_timeout=30,
            _debug_config=config,
            exc_info=True,
        )

    # Example 5: Pydantic ValidationError with logger.exception()
    logger.info('\nExample 5: Pydantic validation error')
    try:
        config_data = {
            'host': 'localhost',
            'port': 'not-a-number',  # Invalid type
            'database': 'mydb',
            # Missing required fields: username, max_connections
        }
        config = DatabaseConfig.model_validate(config_data)
        logger.info('Configuration validated', config=config.model_dump())
    except ValidationError as exc:
        logger.exception('config_validation_failed', errors=exc.errors())
        logger.error('Failed to load database configuration')

    logger.info('\nAll exception examples completed')


if __name__ == '__main__':
    main()
