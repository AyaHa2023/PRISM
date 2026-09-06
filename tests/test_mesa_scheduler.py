import pytest

pytest.importorskip("mesa")

from src.simulation.mesa_scheduler import run_mesa_ticks


def test_mesa_scheduler_runs_ticks():
    days = []
    results = run_mesa_ticks(3, 2, days.append)
    assert days == [1, 2]
    assert [result.active_agents for result in results] == [3, 3]
