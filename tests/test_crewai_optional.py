import pytest

from src.simulation.crewai_workflow import run_crewai_review
from src.simulation.engine import run_simulation


def test_crewai_adapter_has_actionable_optional_dependency_message(monkeypatch):
    result = run_simulation("Mandatory policy affects employees.", days=1, employee_count=2)
    try:
        import crewai  # noqa: F401
    except ImportError:
        with pytest.raises(RuntimeError, match="requirements-optional"):
            run_crewai_review(result)
    else:
        pytest.skip("CrewAI is installed; live orchestration requires a configured model endpoint.")
