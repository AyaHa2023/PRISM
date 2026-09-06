from __future__ import annotations

from dataclasses import dataclass

from ..ontology.policy_ontology import PolicyOntology


@dataclass
class ParameterEffect:
    employee_count: int
    start_morale: int
    start_trust: int
    days: int
    policy_severity: float
    estimated_stress_increase: float
    estimated_trust_drop: float


def compute_parameter_effects(
    employee_count: int,
    start_morale: int,
    start_trust: int,
    days: int,
    policy_severity: float,
) -> ParameterEffect:
    employee_count = max(1, int(employee_count))
    morale_factor = (100 - max(0, min(100, start_morale))) / 100
    trust_factor = (100 - max(0, min(100, start_trust))) / 100
    scale_factor = max(1.0, employee_count / 20)
    time_factor = max(1.0, days / 7)

    stress_rise = (morale_factor * 30 + trust_factor * 20 + policy_severity * 25) * scale_factor * time_factor
    trust_drop = ((policy_severity * 18 + trust_factor * 15) * scale_factor * 0.7) / max(1.0, 1 + (start_trust / 100))

    return ParameterEffect(
        employee_count=employee_count,
        start_morale=start_morale,
        start_trust=start_trust,
        days=days,
        policy_severity=policy_severity,
        estimated_stress_increase=round(stress_rise, 1),
        estimated_trust_drop=round(trust_drop, 1),
    )


def apply_parameter_effects_to_ontology(
    ontology: PolicyOntology,
    employee_count: int,
    start_morale: int,
    start_trust: int,
    days: int,
) -> ParameterEffect:
    return compute_parameter_effects(
        employee_count=employee_count,
        start_morale=start_morale,
        start_trust=start_trust,
        days=days,
        policy_severity=float(getattr(ontology, "severity", 0.5)),
    )
