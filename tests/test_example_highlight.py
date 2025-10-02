"""Tests for example_highlight.py"""


# ============================================================
# Level 0 Tests (Default)
# ============================================================


def test_direct_rich_markup(run_example_highlight):
    """Test example 1: Direct Rich markup"""
    result = run_example_highlight([])
    
    # Should show all highlighted messages at level 0
    assert "Installed 5 packages in 3ms" in result.stdout
    assert "Downloaded 14 files in 2.5s" in result.stdout
    assert "Processing 100 records from database" in result.stdout
    

def test_highlight_helper(run_example_highlight):
    """Test example 2: Using highlight() helper"""
    result = run_example_highlight([])
    
    # The highlight() function should format the message
    assert "Downloaded 14 files in 2.5s" in result.stdout


def test_event_with_highlighted_summary(run_example_highlight):
    """Test example 3: Event-based with highlighted summary"""
    result = run_example_highlight([])
    
    # At level 0, should show summary but not verbose context
    assert "Resolved 42 dependencies with no conflicts in 150ms" in result.stdout
    assert "_verbose_packages" not in result.stdout
    assert "_verbose_registry" not in result.stdout


def test_numbers_and_units(run_example_highlight):
    """Test example 6: Numbers and units highlighting"""
    result = run_example_highlight([])
    
    assert "Cache size: 2.5GB (1,234 entries)" in result.stdout


def test_warning_with_highlight(run_example_highlight):
    """Test example 7: Warning with highlight"""
    result = run_example_highlight([])
    
    # Should show warning message with highlighting
    assert "Rate limit approaching: 95 requests of 100 requests used" in result.stdout
    # Could be marked with WARNING or appear in stderr
    

# ============================================================
# Level 1 Tests (-v)
# ============================================================


def test_verbose_shows_context(run_example_highlight):
    """Test that verbosity level 1 shows additional context"""
    result = run_example_highlight(["-v"])
    
    # Should show the summary
    assert "Resolved 42 dependencies with no conflicts in 150ms" in result.stdout
    
    # Should also show verbose context at level 1
    assert "packages:" in result.stdout
    assert "react, vue, angular" in result.stdout
    assert "registry:" in result.stdout
    assert "https://registry.npmjs.org" in result.stdout


def test_compilation_event_verbose(run_example_highlight):
    """Test example 5: Compilation event with verbose context"""
    result = run_example_highlight(["-v"])
    
    # Summary always shown
    assert "Compilation completed: 95 files successful, 5 files failed" in result.stdout
    
    # Verbose context shown at level 1
    assert "duration:" in result.stdout
    assert "5.2s" in result.stdout
    assert "warnings:" in result.stdout
    assert "12" in result.stdout


# ============================================================
# General Behavior Tests
# ============================================================


def test_all_examples_run_without_error(run_example_highlight):
    """Test that all 7 examples run successfully"""
    result = run_example_highlight([])
    
    # Should complete without error
    assert result.returncode == 0
    assert "Examples completed" in result.stdout


def test_verbosity_flag_accepted(run_example_highlight):
    """Test that -v flag is accepted"""
    result = run_example_highlight(["-v"])
    
    assert result.returncode == 0
    assert "verbosity level: 1" in result.stdout
