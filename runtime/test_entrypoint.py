import json
import os
import subprocess
import sys


RUNTIME = os.path.join(os.path.dirname(__file__), "entrypoint.py")


def run(config, *command):
    env = os.environ.copy()
    env.pop("ATLAS_CONFIG", None)
    if config is not None:
        env["ATLAS_CONFIG"] = json.dumps(config)
    return subprocess.run(
        [sys.executable, RUNTIME, *command],
        env=env,
        text=True,
        capture_output=True,
    )


def test_without_config_preserves_environment():
    result = run(None, sys.executable, "-c", "import os; print(os.getenv('NORMAL_ENV'))")
    assert result.returncode == 0


def test_config_becomes_environment():
    result = run(
        {"DATABASE_URL": "postgres://example", "API_KEY": "secret"},
        sys.executable,
        "-c",
        "import os; print(os.getenv('DATABASE_URL')); print(os.getenv('API_KEY')); print(os.getenv('ATLAS_CONFIG'))",
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["postgres://example", "secret", "None"]


def test_invalid_json_fails():
    env = os.environ.copy()
    env["ATLAS_CONFIG"] = "not-json"
    result = subprocess.run(
        [sys.executable, RUNTIME, sys.executable, "-c", "pass"],
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "invalid ATLAS_CONFIG JSON" in result.stderr


def test_non_string_value_fails():
    result = run({"PORT": 8080}, sys.executable, "-c", "pass")
    assert result.returncode != 0
    assert "must be a string" in result.stderr
