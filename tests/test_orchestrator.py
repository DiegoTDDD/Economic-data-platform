"""Step retries in the orchestrator, with a scripted runner instead of real subprocesses."""

import subprocess

import pytest

import orchestrator


def runner_failing(times_by_script):
    """Each script fails the given number of times, then succeeds."""
    calls = []

    def run(command):
        script = command[-1]
        calls.append(script)
        failures = calls.count(script)
        code = 1 if failures <= times_by_script.get(script, 0) else 0
        return subprocess.CompletedProcess(command, code, stdout="", stderr=f"run {failures}")

    run.calls = calls
    return run


def test_a_step_is_retried_until_it_succeeds():
    waits = []
    run = runner_failing({"x.py": 2})
    assert orchestrator.run_step("X", "x.py", runner=run, sleep=waits.append) == 3
    assert waits == [15, 15]


def test_a_step_that_keeps_failing_stops_the_pipeline():
    run = runner_failing({"analytics_models/bitcoin_ingestion.py": 99})
    with pytest.raises(SystemExit) as exit_info:
        orchestrator.run_pipeline(runner=run, sleep=lambda s: None)
    assert exit_info.value.code == 1
    assert "analytics_models/macro_ingestion.py" not in run.calls
    assert run.calls.count("analytics_models/bitcoin_ingestion.py") == 3


def test_the_whole_pipeline_runs_in_order():
    run = runner_failing({})
    orchestrator.run_pipeline(runner=run, sleep=lambda s: None)
    assert run.calls == [script for _, script in orchestrator.PIPELINE_STEPS]
