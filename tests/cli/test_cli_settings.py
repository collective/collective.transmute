from collective.transmute.cli import app
from typer.testing import CliRunner


runner = CliRunner()


def test_run_app(test_dir):
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 0
    stdout = result.stdout
    assert "Settings used by this application" in stdout


def test_run_app_no_transmute(test_dir):
    config = test_dir / "transmute.toml"
    config.unlink(missing_ok=True)  # Remove the config file if it exists
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 1
    stdout = result.stdout
    assert "Did not find a transmute.toml file" in stdout
    assert "You should first run 'uv run transmute generate'" in stdout
