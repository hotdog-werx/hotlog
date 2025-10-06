import pytest

from hotlog import configure_logging, get_logger, maybe_live_logging
from hotlog.live import LiveLogger


@pytest.mark.parametrize(
    ('verbosity', 'display_level', 'should_show'),
    [
        (0, None, True),
        (0, 0, True),
        (0, 1, False),
        (1, 1, True),
        (1, 2, False),
        (2, 2, True),
    ],
)
def test_display_level_filters_messages(
    capsys: pytest.CaptureFixture,
    verbosity: int,
    display_level: int | None,
    *,
    should_show: bool,
):
    """Verify that _display_level gates messages by active verbosity."""
    configure_logging(verbosity=verbosity)
    capsys.readouterr()  # clear any initial output
    logger = get_logger(__name__)

    kwargs: dict[str, int] = {}
    if display_level is not None:
        kwargs['_display_level'] = display_level

    logger.info('visible-message', **kwargs)
    captured = capsys.readouterr()

    if should_show:
        assert 'visible-message' in captured.out
    else:
        assert 'visible-message' not in captured.out


def test_display_level_not_in_output(capsys: pytest.CaptureFixture):
    """Ensure _display_level does not leak into rendered context."""
    configure_logging(verbosity=2)
    capsys.readouterr()
    logger = get_logger(__name__)

    logger.info('context-check', _display_level=0, detail='value')
    captured = capsys.readouterr()

    assert 'context-check' in captured.out
    assert 'display_level' not in captured.out


@pytest.mark.parametrize('verbosity', [1, 2])
def test_verbose_prefix_stripped(capsys: pytest.CaptureFixture, verbosity: int):
    """_verbose_ prefixes should be removed when rendered."""
    configure_logging(verbosity=verbosity)
    capsys.readouterr()
    logger = get_logger(__name__)

    logger.info('verbose-context', _verbose_my_key='value')
    captured = capsys.readouterr().out

    assert 'verbose-context' in captured
    assert '_verbose_my_key' not in captured
    assert 'my_key:' in captured


def test_debug_prefix_stripped_in_debug_mode(capsys: pytest.CaptureFixture):
    """_debug_ prefixes should be removed when verbosity is 2."""
    configure_logging(verbosity=2)
    capsys.readouterr()
    logger = get_logger(__name__)

    logger.info('debug-context', _debug_state='ready')
    captured = capsys.readouterr().out

    assert 'debug-context' in captured
    assert '_debug_state' not in captured
    assert 'state: ready' in captured


def test_maybe_live_logging_respects_verbosity():
    """maybe_live_logging yields LiveLogger only at verbosity 0."""
    configure_logging(verbosity=0)
    with maybe_live_logging('Downloading...') as live:
        assert isinstance(live, LiveLogger)

    configure_logging(verbosity=1)
    with maybe_live_logging('Downloading...') as live:
        assert live is None
