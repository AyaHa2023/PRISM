from dataclasses import dataclass, field


@dataclass
class Role:
    title: str
    is_internal: bool = True
    priorities: list[str] = field(default_factory=list)


@dataclass
class Personality:
    trait_name: str
    description: str
    stress_sensitivity: float = 1.0  # multiplier when bad news hits


@dataclass
class Metrics:
    stress: int = 30
    trust: int = 80
    loyalty: int = 80

    def clamp(self) -> None:
        self.stress = max(0, min(100, self.stress))
        self.trust = max(0, min(100, self.trust))
        self.loyalty = max(0, min(100, self.loyalty))

    def apply_delta(self, stress_delta: int = 0, trust_delta: int = 0, loyalty_delta: int = 0) -> None:
        self.stress += stress_delta
        self.trust += trust_delta
        self.loyalty += loyalty_delta
        self.clamp()
