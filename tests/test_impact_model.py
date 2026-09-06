from src.ontology.policy_ontology import extract_policy_ontology
from src.simulation.impact_model import compute_parameter_effects


def test_parameter_effects_change_with_population_and_days():
    baseline = compute_parameter_effects(10, 75, 85, 10, 0.7)
    larger = compute_parameter_effects(40, 75, 85, 10, 0.7)
    longer = compute_parameter_effects(40, 75, 85, 30, 0.7)

    assert larger.estimated_stress_increase > baseline.estimated_stress_increase
    assert longer.estimated_stress_increase > larger.estimated_stress_increase
    assert larger.estimated_trust_drop > baseline.estimated_trust_drop


def test_ontology_infers_policy_type_and_severity():
    ontology = extract_policy_ontology("Mandatory return-to-office policy with salary cuts and client risk.")
    assert ontology.policy_type in {"return_to_office", "salary_change", "policy_change"}
    assert ontology.severity >= 0.5
    assert ontology.external_trust_risk in {"medium", "high"}
