"""Step 1.1 + Workflow step 2 — lightweight knowledge graph from seed text."""

from __future__ import annotations

import re
from pathlib import Path

import networkx as nx
import pandas as pd

try:
    import spacy
except ImportError:  # pragma: no cover - optional at runtime
    spacy = None

ENTITY_PATTERNS = [
    (r"\b(Employees?|Managers?|HR|Human Resources|Clients?|Partners?|Consultants?|Leadership|Staff|Teams?)\b", "Stakeholder", re.I),
    (r"\b(IT support|helpdesk|vendor|contract|SLA|salary|bonus|office|remote|hybrid|policy|work from home|return-to-office|morale|trust|stress)\b", "Concept", re.I),
]

RELATION_HINTS = [
    ("reports to", "REPORTS_TO"),
    ("client", "SERVES"),
    ("partner", "CONTRACTED_WITH"),
    ("hr", "GOVERNED_BY"),
    ("manager", "MANAGED_BY"),
    ("policy", "AFFECTS"),
    ("stress", "IMPACTS"),
    ("morale", "IMPACTS"),
    ("trust", "AFFECTS"),
]

CANONICAL_ALIASES = {
    "employee": "Employees",
    "employees": "Employees",
    "manager": "Managers",
    "managers": "Managers",
    "hr": "HR",
    "human resources": "HR",
    "client": "Clients",
    "clients": "Clients",
    "partner": "Partners",
    "partners": "Partners",
    "consultant": "Consultants",
    "consultants": "Consultants",
    "leadership": "Leadership",
    "staff": "Staff",
    "teams": "Teams",
    "team": "Teams",
    "policy": "Policy",
    "return-to-office": "Return-to-office policy",
    "return to office": "Return-to-office policy",
    "salary": "Salary",
    "bonus": "Bonus",
    "office": "Office",
    "remote": "Remote work",
    "hybrid": "Hybrid work",
    "morale": "Morale",
    "trust": "Trust",
    "stress": "Stress",
    "contract": "Contract",
    "sla": "SLA",
    "vendor": "Vendor",
    "helpdesk": "IT support",
    "it support": "IT support",
}


def load_seed_text(path: Path) -> str:
    if not path.exists():
        return ""
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def _normalize_token(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().lower()).strip(" .;,:!?()[]{}\n\r\t")


def _canonicalize_entity(raw: str) -> tuple[str, str]:
    token = _normalize_token(raw)
    if not token:
        return "", "Concept"

    alias = CANONICAL_ALIASES.get(token)
    if alias:
        return alias, "Concept"

    if token.startswith("human resources"):
        return "HR", "Stakeholder"

    if token.endswith("policy"):
        return token.title(), "Event"

    if token in {"employee", "employees"}:
        return "Employees", "Stakeholder"

    if token in {"manager", "managers"}:
        return "Managers", "Stakeholder"

    if token in {"client", "clients"}:
        return "Clients", "Stakeholder"

    if token in {"partner", "partners"}:
        return "Partners", "Stakeholder"

    if token in {"consultant", "consultants"}:
        return "Consultants", "Stakeholder"

    if token in {"stress", "morale", "trust"}:
        return token.title(), "Concept"

    return token.title(), "Concept"


def _regex_extract_entities(text: str) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for item in ENTITY_PATTERNS:
        pattern, label = item[0], item[1]
        flags = item[2] if len(item) > 2 else 0
        for match in re.finditer(pattern, text, flags=flags):
            token = match.group(1).strip()
            key, canonical_label = _canonicalize_entity(token)
            if not key:
                continue
            if key.lower() not in {k.lower() for k in found}:
                found[key] = canonical_label or label
    return [(key, val) for key, val in found.items()]


def _spacy_extract_entities(text: str) -> list[tuple[str, str]]:
    if spacy is None:
        return []

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        return []

    doc = nlp(text)
    found: dict[str, str] = {}
    for ent in doc.ents:
        token = ent.text.strip()
        key, label = _canonicalize_entity(token)
        if key:
            found[key] = label

    # spaCy does not reliably catch common organizational nouns like "employees".
    # So we always combine with regex extraction to keep the KG stable and useful.
    for key, label in _regex_extract_entities(text):
        found.setdefault(key, label)

    return [(key, val) for key, val in found.items()]


def extract_policy_entities(text: str) -> list[tuple[str, str]]:
    """Return canonical policy entities using spaCy first and a regex fallback."""
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    entities = _spacy_extract_entities(cleaned)
    if entities:
        return entities
    return _regex_extract_entities(cleaned)


def extract_entities(text: str) -> list[tuple[str, str]]:
    return extract_policy_entities(text)


def _edge_relation(source: str, target: str, text: str) -> str:
    s = source.lower()
    t = target.lower()
    lower = text.lower()

    if "policy" in s or "policy" in t:
        return "AFFECTS"
    if ("employee" in s or "employee" in t) and ("manager" in s or "manager" in t):
        return "REPORTS_TO"
    if ("client" in s or "client" in t) and ("partner" in s or "partner" in t):
        return "TRUSTS"
    if "hr" in s or "hr" in t:
        return "GOVERNED_BY"
    if ("stress" in s or "stress" in t) or ("morale" in s or "morale" in t):
        return "IMPACTS"
    if "trust" in s or "trust" in t:
        return "AFFECTS"
    if any(hint in lower for hint in ["client", "partner", "contract", "sla"]):
        return "DEPENDS_ON"
    for hint, rel in RELATION_HINTS:
        if hint in lower and (hint in s or hint in t):
            return rel
    return "RELATED_TO"


def build_knowledge_graph(text: str) -> nx.DiGraph:
    """Knowledge graph with a spaCy-first entity layer and regex fallback."""
    graph = nx.DiGraph()
    entities = extract_policy_entities(text)

    for name, etype in entities:
        graph.add_node(name, entity_type=etype)

    if not entities:
        graph.add_node("Policy", entity_type="Event")
        return graph

    for i, (source, _) in enumerate(entities):
        for target, _ in entities[i + 1 :]:
            relation = _edge_relation(source, target, text)
            graph.add_edge(source, target, relation=relation)

    policy_nodes = [name for name, etype in entities if "policy" in name.lower()]
    if not policy_nodes:
        graph.add_node("Policy", entity_type="Event")
        for name, _ in entities[:3]:
            graph.add_edge("Policy", name, relation="AFFECTS")
    else:
        policy_name = policy_nodes[0]
        for name, _ in entities[:3]:
            if name != policy_name:
                graph.add_edge(policy_name, name, relation="AFFECTS")

    return graph


def graph_to_dataframe(graph: nx.DiGraph) -> pd.DataFrame:
    rows = []
    for u, v, data in graph.edges(data=True):
        rows.append({"source": u, "target": v, "relation": data.get("relation", "RELATED_TO")})
    return pd.DataFrame(rows)
