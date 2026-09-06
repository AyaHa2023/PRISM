"""Streamlit dashboard — Part 5 of Build.pdf."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_layer.state_db import StateDatabase
from src.graph.knowledge_graph import build_knowledge_graph, graph_to_dataframe, load_seed_text
from src.graph.scenario_visualization import scenario_graph_dot
from src.graph.typed_graph import build_typed_policy_graph, summarize_typed_graph
from src.ui.interactive_graph import graph_data_from_result, interactive_scenario_graph
from src.simulation.agent_chat import ask_agent
from src.simulation.engine import run_simulation
from src.simulation.group_conversation import run_group_conversation
from src.simulation.multi_agent_workflow import run_multi_agent_report
from src.simulation.crewai_workflow import run_crewai_review
from src.simulation.reporting import generate_report
from src.simulation.reporter_chat import ask_reporter
from src.simulation.scenario_compare import compare_scenarios
from src.simulation.scenario_generator import generate_policy_context, policy_context_text

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "prism.db"
SEED_DIR = ROOT / "data" / "seed"
SCENARIOS_PATH = ROOT / "data" / "scenarios" / "scenarios.json"
PHASE2_SCENARIOS_PATH = ROOT / "data" / "scenarios" / "scenarios_phase2.json"


st.set_page_config(page_title="PwC Prism", layout="wide", page_icon="🛡")

st.title("🛡 PwC Prism — Workplace Policy Simulator")
st.caption("Student prototype inspired by MiroFish · ABM + network graph · organizational health")

# --- Sidebar: manual seed (MiroFish sliders) ---
st.sidebar.title("Simulation Setup")
st.sidebar.markdown("### Initial base variables (manual)")
start_morale = st.sidebar.slider("Starting employee morale", 0, 100, 75)
start_trust = st.sidebar.slider("Starting client trust", 0, 100, 85)
sim_days = st.sidebar.slider("Simulation days", 3, 14, 10)
employee_count = st.sidebar.slider("Internal employees", 2, 40, 5)

st.sidebar.markdown("### Agent brain")
use_live_llm = st.sidebar.toggle("Use local Ollama LLM", value=False)
llm_model = st.sidebar.text_input("Ollama model", value="llama3.1:latest")
if use_live_llm:
    st.sidebar.caption("Live mode uses localhost:11434 and falls back to mock responses if a request fails.")
else:
    st.sidebar.caption("Mock mode is deterministic and does not require Ollama.")

graph_backend = st.sidebar.selectbox("Policy graph backend", ["networkx", "neo4j"], index=0)
graph_database = st.sidebar.text_input("Neo4j database", value="prismDB")
if graph_backend == "neo4j":
    st.sidebar.caption("Neo4j mode requires NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, and NEO4J_DATABASE.")

st.sidebar.markdown("### AI scenario studio")
if st.sidebar.button("Generate AI policy/context", type="primary"):
    with st.spinner("Generating a concrete organizational policy scenario…"):
        generated_context = generate_policy_context(use_mock=not use_live_llm, model=llm_model)
    st.session_state["generated_context"] = generated_context
    st.session_state["generated_policy"] = generated_context["policy"]
generated_context = st.session_state.get("generated_context")
if generated_context:
    st.sidebar.caption(generated_context["title"])
    st.sidebar.json(generated_context)

st.sidebar.markdown("### Seed document")
seed_files = list(SEED_DIR.glob("*")) if SEED_DIR.exists() else []
seed_choice = st.sidebar.selectbox(
    "Load example policy",
    ["Custom text"] + [f.name for f in seed_files],
)

if seed_choice != "Custom text":
    seed_text = load_seed_text(SEED_DIR / seed_choice)
else:
    seed_text = ""

policy_default = seed_text.split("\n\n")[0][:200] if seed_text else "Mandatory return-to-office 4 days per week"

policy_input = st.text_area(
    "Define policy change or decision",
    value=policy_default if seed_choice != "Custom text" else "Mandatory return-to-office 4 days per week",
    height=120,
)
if st.session_state.get("generated_policy"):
    policy_input = st.session_state["generated_policy"]

tab_run, tab_compare, tab_chat, tab_multi, tab_kg, tab_docs = st.tabs(
    ["Run simulation", "Compare scenarios", "Agent chat", "Multi-agent review", "Knowledge graph", "Student journal"]
)

with tab_kg:
    st.subheader("Step 1.1–1.2 · Knowledge graph from seed text")
    combined = policy_input + "\n" + (seed_text or "")
    kg = build_knowledge_graph(combined)
    typed_kg = build_typed_policy_graph(combined)
    st.write(
        f"**Legacy entities:** {kg.number_of_nodes()} · **Typed nodes:** {typed_kg.number_of_nodes()} "
        f"· **Typed relations:** {typed_kg.number_of_edges()}"
    )
    if kg.number_of_edges():
        st.dataframe(graph_to_dataframe(kg), use_container_width=True)
    else:
        st.info("Add more stakeholder keywords in your policy text to populate the graph.")
    st.markdown("### Typed graph context")
    st.code(summarize_typed_graph(typed_kg))
    last_result_for_graph = st.session_state.get("last_result")
    if last_result_for_graph:
        st.markdown("### Scenario graph: actors, topics, relationships, and messages")
        graph_data = graph_data_from_result(last_result_for_graph)
        graph_state = st.session_state.get("graph_positions", {})
        graph_result = interactive_scenario_graph(graph_data, graph_state)
        if graph_result and getattr(graph_result, "positions", None):
            st.session_state["graph_positions"] = graph_result.positions
        st.caption("Drag nodes, use the mouse wheel to zoom, and select a node to inspect its role and current metrics.")
        with st.expander("Static export view"):
            st.graphviz_chart(scenario_graph_dot(last_result_for_graph), width="stretch")

with tab_run:
    col1, col2 = st.columns([1, 2])

    with col1:
        run_btn = st.button("Run simulation loop", type="primary", width="stretch")
        if SCENARIOS_PATH.exists():
            with st.expander("Preset scenarios (from coursework PDF)"):
                scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
                for s in scenarios:
                    st.markdown(f"**{s['id']} — {s['name']}:** {s['policy']}")

    with col2:
        if run_btn:
            db = StateDatabase(DB_PATH)
            feed = st.container()
            steps_log: list[dict] = []

            def on_step(step):
                steps_log.append(
                    {
                        "day": step.day,
                        "quadrant": step.quadrant,
                        "agent": step.agent_name,
                        "message": step.message,
                        "stress": step.stress,
                        "trust": step.trust,
                        "sentiment": step.sentiment,
                    }
                )

            with st.spinner("Running 4-quadrant ABM loop…"):
                result = run_simulation(
                    policy_input,
                    start_morale=start_morale,
                    start_trust=start_trust,
                    days=sim_days,
                    employee_count=employee_count,
                    db=db,
                    use_mock_llm=not use_live_llm,
                    llm_model=llm_model,
                    graph_backend=graph_backend,
                    graph_database=graph_database,
                    on_step=on_step,
                )

            st.success(f"Completed {sim_days}-day simulation · {len(steps_log)} events logged")
            st.session_state["last_result"] = result
            st.session_state["last_policy"] = policy_input

            history = db.load_history()
            if not history.empty:
                fig, ax = plt.subplots(figsize=(8, 3))
                for name, grp in history.groupby("agent_name"):
                    ax.plot(grp["day"], grp["stress"], marker="o", label=f"{name} stress")
                ax.set_xlabel("Day")
                ax.set_ylabel("Stress (0–100)")
                ax.legend(fontsize=7, loc="upper left")
                ax.set_ylim(0, 100)
                st.pyplot(fig)

            st.markdown("### Live feed")
            df_steps = pd.DataFrame(steps_log)
            st.dataframe(df_steps, use_container_width=True, height=320)

            report = generate_report(policy_input, result, use_mock=not use_live_llm, model=llm_model)
            st.session_state["last_report"] = report
            st.markdown("### Structured report agent")
            st.caption(f"Source: {report.source} · confidence: {report.confidence:.0%}")
            st.subheader(report.headline)
            st.write(report.executive_summary)
            st.write("**Key risks**")
            for risk in report.key_risks:
                st.write(f"- {risk}")
            st.write("**Recommended actions**")
            for action in report.recommended_actions:
                st.write(f"- {action}")
            st.write("**Narrative paths**")
            for path in report.narrative_paths:
                st.write(f"- {path}")
            st.write("**Turning points**")
            for point in report.turning_points:
                st.write(f"- {point}")
            st.write("**Confidence gaps**")
            for gap in report.confidence_gaps:
                st.write(f"- {gap}")
            st.download_button(
                "Download report JSON",
                data=json.dumps(report.to_dict(), indent=2),
                file_name="prism_simulation_report.json",
                mime="application/json",
            )
            st.markdown("### Formal and informal communication history")
            history_messages = db.load_messages()
            if not history_messages.empty:
                channel_filter = st.multiselect(
                    "Channels",
                    sorted(history_messages["channel"].dropna().unique().tolist()),
                    default=sorted(history_messages["channel"].dropna().unique().tolist()),
                    key="run_channel_filter",
                )
                visible_messages = history_messages[history_messages["channel"].isin(channel_filter)]
                st.dataframe(visible_messages, width="stretch", height=300)
                st.download_button(
                    "Download communication history CSV",
                    data=visible_messages.to_csv(index=False),
                    file_name="prism_communication_history.csv",
                    mime="text/csv",
                )
        else:
            st.info("Configure sliders and policy, then click **Run simulation loop**.")

with tab_compare:
    st.subheader("Step 7 · Compare policy outcomes")
    if SCENARIOS_PATH.exists():
        scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
        if PHASE2_SCENARIOS_PATH.exists():
            scenarios += json.loads(PHASE2_SCENARIOS_PATH.read_text(encoding="utf-8"))
        selected_ids = st.multiselect(
            "Scenarios to compare",
            options=[scenario["id"] for scenario in scenarios],
            default=[scenario["id"] for scenario in scenarios[:2]],
        )
        selected = [scenario for scenario in scenarios if scenario["id"] in selected_ids]
        if st.button("Run scenario comparison", type="primary") and selected:
            with st.spinner("Running comparable scenarios…"):
                comparison = compare_scenarios(
                    selected,
                    start_morale=start_morale,
                    start_trust=start_trust,
                    days=sim_days,
                    employee_count=employee_count,
                    use_mock_llm=not use_live_llm,
                    llm_model=llm_model,
                )
            st.dataframe(comparison, width="stretch")
            st.bar_chart(comparison.set_index("scenario")[['average_stress', 'minimum_external_trust']])
            st.download_button(
                "Download comparison CSV",
                data=comparison.to_csv(index=False),
                file_name="prism_scenario_comparison.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download comparison JSON",
                data=comparison.to_json(orient="records", indent=2),
                file_name="prism_scenario_comparison.json",
                mime="application/json",
            )
        elif not selected:
            st.info("Select at least one scenario.")
    else:
        st.info("No scenario file found.")

with tab_chat:
    st.subheader("Step 8 · Talk to an agent after simulation")
    last_result = st.session_state.get("last_result")
    if last_result and last_result.employees:
        selected_agent_name = st.selectbox("Agent", [agent.name for agent in last_result.employees])
        selected_agent = next(agent for agent in last_result.employees if agent.name == selected_agent_name)
        question = st.chat_input("Ask this agent about the policy or their reaction")
        if question:
            db = StateDatabase(DB_PATH)
            answer = ask_agent(
                selected_agent,
                question,
                db=db,
                use_mock=not use_live_llm,
                model=llm_model,
            )
            st.chat_message("user").write(question)
            st.chat_message("assistant").write(answer["message"])
            st.caption(f"Sentiment: {answer.get('sentiment', 'neutral')}")
        st.markdown("### Ask the forecast reporter")
        last_report = st.session_state.get("last_report")
        reporter_question = st.text_input("Ask why the forecast changed or challenge a risk", key="reporter_question")
        if st.button("Ask reporter", key="ask_reporter") and reporter_question and last_report:
            st.write(f"**Question:** {reporter_question}")
            st.write(ask_reporter(reporter_question, last_report, use_mock=not use_live_llm, model=llm_model))
    else:
        st.info("Run a simulation first to activate agent chat.")
with tab_multi:
    st.subheader("Multi-agent policy review")
    last_result = st.session_state.get("last_result")

    if last_result:
        review_mode = st.radio(
            "Review engine",
            ["Native workflow", "CrewAI"],
            horizontal=True,
        )

        if review_mode == "Native workflow":
            if st.button("Run specialist review", type="primary"):
                with st.spinner("Running employee, client-risk, and network specialists…"):
                    specialist_report = run_multi_agent_report(
                        last_result,
                        use_mock=not use_live_llm,
                        model=llm_model,
                    )
                st.session_state["last_multi_report"] = specialist_report

            specialist_report = st.session_state.get("last_multi_report")

            if specialist_report:
                st.write(specialist_report.synthesis)
                st.caption(
                    f"Overall sentiment: {specialist_report.overall_sentiment} "
                    f"· confidence: {specialist_report.confidence:.0%}"
                )
                st.dataframe(
                    pd.DataFrame(
                        [finding.to_dict() for finding in specialist_report.findings]
                    ),
                    width="stretch",
                )

                st.download_button(
                    "Download multi-agent review JSON",
                    data=json.dumps(specialist_report.to_dict(), indent=2),
                    file_name="prism_multi_agent_review.json",
                    mime="application/json",
                )

        else:
            if st.button("Run CrewAI review", type="primary"):
                with st.spinner("Running CrewAI specialist review…"):
                    crewai_report = run_crewai_review(
                        last_result,
                        model=f"ollama/{llm_model}",
                    )
                st.session_state["last_crewai_report"] = crewai_report

            crewai_report = st.session_state.get("last_crewai_report")

            if crewai_report:
                st.caption("Source: CrewAI + Ollama")
                st.write(crewai_report["result"])

                st.download_button(
                    "Download CrewAI review JSON",
                    data=json.dumps(crewai_report, indent=2),
                    file_name="prism_crewai_review.json",
                    mime="application/json",
                )

        st.markdown("### Employee and partner group conversation")
        conversation_topic = st.text_input(
            "Conversation topic",
            value=st.session_state.get("last_policy", policy_input),
        )
        conversation_rounds = st.slider("Conversation rounds", 1, 4, 2)
        if st.button("Run graph-constrained conversation", type="primary"):
            db = StateDatabase(DB_PATH)
            with st.spinner("Agents are responding through workplace relationships…"):
                conversation = run_group_conversation(
                    [*last_result.employees, *last_result.partners],
                    last_result.graph,
                    conversation_topic,
                    rounds=conversation_rounds,
                    use_mock=not use_live_llm,
                    model=llm_model,
                    db=db,
                )
            st.session_state["last_conversation"] = conversation

        conversation = st.session_state.get("last_conversation")
        if conversation:
            st.dataframe(
                pd.DataFrame([turn.to_dict() for turn in conversation.turns]),
                width="stretch",
            )
            st.download_button(
                "Download group conversation JSON",
                data=json.dumps(conversation.to_dict(), indent=2),
                file_name="prism_group_conversation.json",
                mime="application/json",
            )

    else:
        st.info("Run a simulation first to activate the multi-agent review.")
with tab_docs:
    journal_path = ROOT / "STUDENT_JOURNAL.md"
    if journal_path.exists():
        st.markdown(journal_path.read_text(encoding="utf-8"))
    else:
        st.warning("STUDENT_JOURNAL.md not found.")
