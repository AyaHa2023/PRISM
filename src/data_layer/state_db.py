"""Step 1.3 — SQLite time-series log for agent metrics."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from ..models.personas import AgentExternal, AgentInternal


class StateDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    stress INTEGER NOT NULL,
                    trust INTEGER NOT NULL,
                    loyalty INTEGER NOT NULL,
                    last_message TEXT,
                    quadrant TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_text TEXT NOT NULL,
                    start_morale INTEGER,
                    start_trust INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    quadrant TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_profiles (
                    agent_name TEXT PRIMARY KEY,
                    profile_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    text TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    stress_delta INTEGER DEFAULT 0,
                    trust_delta INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def log_metrics(
        self,
        day: int,
        agents: list[AgentInternal | AgentExternal],
        last_messages: dict[str, str] | None = None,
        quadrant: str = "",
    ) -> None:
        last_messages = last_messages or {}
        with self._connect() as conn:
            for agent in agents:
                agent_type = "internal" if isinstance(agent, AgentInternal) else "external"
                conn.execute(
                    """
                    INSERT INTO agent_metrics
                    (day, agent_name, role, agent_type, stress, trust, loyalty, last_message, quadrant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        day,
                        agent.name,
                        agent.role.title,
                        agent_type,
                        agent.metrics.stress,
                        agent.metrics.trust,
                        agent.metrics.loyalty,
                        last_messages.get(agent.name, ""),
                        quadrant,
                    ),
                )

    def log_run(self, policy_text: str, start_morale: int, start_trust: int) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO simulation_runs (policy_text, start_morale, start_trust) VALUES (?, ?, ?)",
                (policy_text, start_morale, start_trust),
            )
            return int(cur.lastrowid)

    def load_history(self) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query("SELECT * FROM agent_metrics ORDER BY day, agent_name", conn)

    def clear_metrics(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM agent_metrics")

    def store_agent_memory(self, agent_name: str, memory_type: str, summary: str, quadrant: str = "") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO agent_memory (agent_name, memory_type, summary, quadrant) VALUES (?, ?, ?, ?)",
                (agent_name, memory_type, summary, quadrant),
            )
            return int(cur.lastrowid)

    def get_agent_memory(self, agent_name: str, limit: int = 10) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT agent_name, memory_type, summary, quadrant, created_at FROM agent_memory WHERE agent_name = ? ORDER BY id DESC LIMIT ?",
                (agent_name, limit),
            ).fetchall()
        return [
            {
                "agent_name": row[0],
                "memory_type": row[1],
                "summary": row[2],
                "quadrant": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]

    def build_agent_context(self, agent_name: str, limit: int = 5) -> str:
        memories = self.get_agent_memory(agent_name, limit=limit)
        if not memories:
            return f"{agent_name}: no stored memory yet."
        return " | ".join(f"{m['quadrant']}: {m['summary']}" for m in memories)

    def store_agent_profile(self, agent_name: str, profile: dict) -> None:
        import json

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_profiles (agent_name, profile_json, source)
                VALUES (?, ?, ?)
                ON CONFLICT(agent_name) DO UPDATE SET profile_json=excluded.profile_json,
                    source=excluded.source, updated_at=CURRENT_TIMESTAMP
                """,
                (agent_name, json.dumps(profile), profile.get("source", "unknown")),
            )

    def load_agent_profile(self, agent_name: str) -> dict | None:
        import json

        with self._connect() as conn:
            row = conn.execute(
                "SELECT profile_json FROM agent_profiles WHERE agent_name = ?",
                (agent_name,),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def store_message(self, message: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_messages
                (day, sender, receiver, channel, text, sentiment, stress_delta, trust_delta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message["day"], message["sender"], message["receiver"], message["channel"],
                    message["text"], message["sentiment"], message.get("stress_delta", 0),
                    message.get("trust_delta", 0),
                ),
            )

    def get_messages_for_agent(self, agent_name: str, limit: int = 10) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT day, sender, receiver, channel, text, sentiment FROM agent_messages "
                "WHERE receiver = ? ORDER BY id DESC LIMIT ?",
                (agent_name, limit),
            ).fetchall()
        return [
            {"day": r[0], "sender": r[1], "receiver": r[2], "channel": r[3], "text": r[4], "sentiment": r[5]}
            for r in rows
        ]

    def load_messages(self, limit: int = 500) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query(
                "SELECT day, sender, receiver, channel, text, sentiment, stress_delta, trust_delta, created_at "
                "FROM agent_messages ORDER BY id DESC LIMIT ?",
                conn,
                params=(limit,),
            )
