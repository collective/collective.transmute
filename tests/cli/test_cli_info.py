from collective.transmute.cli import app
from typer.testing import CliRunner


runner = CliRunner()


def _write_converter(test_dir, table: str) -> None:
    path = test_dir / "transmute.toml"
    path.write_text(path.read_text() + f"\n[steps.blocks.converter]\n{table}\n")


def test_info_lists_block_types_by_default(test_dir):
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Volto blocks:" in result.stdout
    assert " - codeBlock: disabled (default), package:" in result.stdout
    assert " - slateTable: enabled (default), package:" in result.stdout


def test_info_reflects_converter_table(test_dir):
    _write_converter(test_dir, "codeBlock = true\nslateTable = false")
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert " - codeBlock: enabled (transmute.toml), package:" in result.stdout
    assert " - slateTable: disabled (transmute.toml), package:" in result.stdout


def test_invalid_converter_stops_cli(test_dir):
    _write_converter(test_dir, "nope = true")
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 1
    assert "Unknown block type nope" in result.stdout
    assert "Volto blocks:" not in result.stdout
