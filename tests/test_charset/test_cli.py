"""Tests for the uniff_charset.cli module."""

from click.testing import CliRunner
from uniff_charset.cli import info


def test_cli_info():
    """Test the info command."""
    runner = CliRunner()
    result = runner.invoke(info)

    # Check that the command executed successfully
    assert result.exit_code == 0

    # Check that the output contains expected text
    assert "uniff-charset: Unicode Data Format Information" in result.output
    assert "Available output formats:" in result.output
    assert "CSV" in result.output
    assert "JSON" in result.output
    assert "Lua" in result.output
