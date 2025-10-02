"""Tests for example_quickstart.py"""


# ============================================================
# Level 0 Tests (Default)
# ============================================================


def test_quickstart_basic_messages(run_example_quickstart):
    """Test basic messages at verbosity level 0"""
    result = run_example_quickstart([])
    
    # Basic messages should appear
    assert "Application starting" in result.stdout
    assert "version: 1.0.0" in result.stdout
    assert "Loaded 50 plugins in 120ms" in result.stdout


def test_quickstart_prefix_filtering_level_0(run_example_quickstart):
    """Test that _verbose_ and _debug_ are filtered at level 0"""
    result = run_example_quickstart([])
    
    # Base context shown
    assert "Configuration loaded" in result.stdout
    assert "env: production" in result.stdout
    
    # Verbose/debug context hidden
    assert "config_file:" not in result.stdout
    assert "raw_config:" not in result.stdout


def test_quickstart_tool_execution_level_0(run_example_quickstart):
    """Test tool execution with custom prefix at level 0"""
    result = run_example_quickstart([])
    
    # Should use 'myapp' prefix
    assert "myapp[docker-build]" in result.stdout
    assert "docker build -t myapp:latest ." in result.stdout
    
    # Verbose context should not appear
    assert "_verbose_layers" not in result.stdout


def test_quickstart_warning_shown(run_example_quickstart):
    """Test that warnings are always shown"""
    result = run_example_quickstart([])
    
    assert "API rate limit at 80%" in result.stdout
    assert "current: 80" in result.stdout
    assert "limit: 100" in result.stdout


# ============================================================
# Level 1 Tests (-v)
# ============================================================


def test_quickstart_verbose_context_level_1(run_example_quickstart):
    """Test that _verbose_ context is shown at level 1"""
    result = run_example_quickstart(["-v"])
    
    # Verbose context should appear
    assert "Configuration loaded" in result.stdout
    assert "config_file: /etc/myapp/config.yaml" in result.stdout
    
    # Tool verbose context
    assert "myapp[docker-build]" in result.stdout
    assert "layers: 12" in result.stdout
    
    # Debug context should NOT appear
    assert "raw_config:" not in result.stdout
    assert "build_context:" not in result.stdout


def test_quickstart_live_logging_verbose(run_example_quickstart):
    """Test that live logging messages are visible at level 1"""
    result = run_example_quickstart(["-v"])
    
    # Live messages should be visible
    assert "Downloaded package-1" in result.stdout
    assert "Downloaded package-2" in result.stdout
    assert "Downloaded package-3" in result.stdout
    
    # Verbose context from live logging
    assert "size: 2MB" in result.stdout
    assert "size: 4MB" in result.stdout
    assert "size: 6MB" in result.stdout


# ============================================================
# Level 2 Tests (-vv)
# ============================================================


def test_quickstart_debug_context_level_2(run_example_quickstart):
    """Test that _debug_ context is shown at level 2"""
    result = run_example_quickstart(["-v", "-v"])
    
    # All context including debug
    assert "Configuration loaded" in result.stdout
    assert "config_file: /etc/myapp/config.yaml" in result.stdout
    assert "raw_config:" in result.stdout
    
    # Tool debug context
    assert "myapp[docker-build]" in result.stdout
    assert "layers: 12" in result.stdout
    assert "build_context: /tmp/build-123" in result.stdout


# ============================================================
# General Behavior Tests
# ============================================================


def test_quickstart_highlight_helper(run_example_quickstart):
    """Test that highlight() helper works"""
    result = run_example_quickstart([])
    
    # Highlighted messages should appear
    assert "Loaded 50 plugins in 120ms" in result.stdout
    assert "Downloaded 3 packages successfully" in result.stdout


def test_quickstart_tips_shown(run_example_quickstart):
    """Test that help tips are shown"""
    result = run_example_quickstart([])
    
    assert "Tips:" in result.stdout
    assert "-v for verbose" in result.stdout or "_verbose_" in result.stdout
    assert "-vv for debug" in result.stdout or "_debug_" in result.stdout


def test_quickstart_all_verbosity_levels(run_example_quickstart):
    """Test that all verbosity levels work"""
    result_0 = run_example_quickstart([])
    result_1 = run_example_quickstart(["-v"])
    result_2 = run_example_quickstart(["-v", "-v"])
    
    assert result_0.returncode == 0
    assert result_1.returncode == 0
    assert result_2.returncode == 0
    
    assert "verbosity level: 0" in result_0.stdout
    assert "verbosity level: 1" in result_1.stdout
    assert "verbosity level: 2" in result_2.stdout


def test_quickstart_completes_successfully(run_example_quickstart):
    """Test that quickstart example completes without error"""
    result = run_example_quickstart([])
    
    assert result.returncode == 0
    assert "Quick Start Example" in result.stdout
