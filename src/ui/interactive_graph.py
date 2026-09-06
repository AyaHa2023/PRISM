from __future__ import annotations

import json
from typing import Any

import streamlit as st


_GRAPH_HTML = """
<div class="prism-graph-shell">
  <div class="prism-graph-toolbar">
    <button id="reset" type="button">Reset layout</button>
    <span id="selected">Select a node</span>
  </div>
  <svg id="canvas" viewBox="0 0 1000 620" aria-label="Interactive Prism scenario graph"></svg>
</div>
"""

_GRAPH_CSS = """
.prism-graph-shell { border: 1px solid var(--st-border-color, #cbd5e1); border-radius: 8px; overflow: hidden; background: var(--st-secondary-background-color, #f8fafc); }
.prism-graph-toolbar { display: flex; gap: 12px; align-items: center; padding: 8px 12px; color: var(--st-text-color, #1e293b); font: 13px sans-serif; }
.prism-graph-toolbar button { border: 1px solid #94a3b8; border-radius: 5px; padding: 6px 10px; background: var(--st-background-color, white); color: var(--st-text-color, #1e293b); cursor: pointer; }
#canvas { width: 100%; min-height: 520px; touch-action: none; cursor: grab; }
.edge { stroke: #94a3b8; stroke-width: 1.5; opacity: .8; }
.message-edge { stroke: #dc2626; stroke-dasharray: 6 4; stroke-width: 2; }
.node { stroke: #334155; stroke-width: 1.5; cursor: grab; }
.node.selected { stroke: #0f172a; stroke-width: 4; }
.node-label { font: 12px sans-serif; pointer-events: none; fill: #0f172a; }
.edge-label { font: 9px sans-serif; fill: #475569; pointer-events: none; }
"""

_GRAPH_JS = """
export default function(component) {
  const { data, parentElement, setStateValue, setTriggerValue } = component;
  const svg = parentElement.querySelector('#canvas');
  const selected = parentElement.querySelector('#selected');
  const reset = parentElement.querySelector('#reset');
  if (!svg || !data) return;

  const key = 'positions';
  const saved = data.positions || {};
  const nodes = (data.nodes || []).map((node, index) => ({
    ...node,
    x: saved[node.id]?.x ?? 180 + (index % 5) * 170,
    y: saved[node.id]?.y ?? 130 + Math.floor(index / 5) * 150,
  }));
  const byId = Object.fromEntries(nodes.map(node => [node.id, node]));
  const edges = data.edges || [];
  let dragging = null;
  let selectedId = null;
  let scale = 1;
  let panX = 0;
  let panY = 0;

  function resetLayout() {
    nodes.forEach((node, index) => {
      node.x = 180 + (index % 5) * 170;
      node.y = 130 + Math.floor(index / 5) * 150;
    });
    emitPositions();
    render();
  }

  function emitPositions() {
    const positions = Object.fromEntries(nodes.map(node => [node.id, {x: node.x, y: node.y}]));
    setStateValue(key, positions);
  }

  function point(event) {
    const rect = svg.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) / rect.width * 1000,
      y: (event.clientY - rect.top) / rect.height * 620,
    };
  }

  function render() {
    svg.innerHTML = '';
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('transform', `translate(${panX} ${panY}) scale(${scale})`);
    const edgeLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    edges.forEach(edge => {
      const source = byId[edge.source]; const target = byId[edge.target];
      if (!source || !target) return;
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', source.x); line.setAttribute('y1', source.y);
      line.setAttribute('x2', target.x); line.setAttribute('y2', target.y);
      line.setAttribute('class', edge.kind === 'message' ? 'edge message-edge' : 'edge');
      line.setAttribute('marker-end', 'url(#arrow)');
      edgeLayer.appendChild(line);
      const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', (source.x + target.x) / 2); label.setAttribute('y', (source.y + target.y) / 2 - 4);
      label.setAttribute('class', 'edge-label'); label.textContent = edge.label || '';
      edgeLayer.appendChild(label);
    });
    group.appendChild(edgeLayer);
    nodes.forEach(node => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${node.x} ${node.y})`);
      g.setAttribute('data-id', node.id);
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', node.kind === 'agent' ? 38 : 32);
      circle.setAttribute('fill', node.color || '#dbeafe');
      circle.setAttribute('class', selectedId === node.id ? 'node selected' : 'node');
      g.appendChild(circle);
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle'); text.setAttribute('dy', '4'); text.setAttribute('class', 'node-label');
      text.textContent = node.label;
      g.appendChild(text);
      g.addEventListener('pointerdown', event => {
        event.stopPropagation(); dragging = {node, offset: point(event)}; selectedId = node.id;
        selected.textContent = `${node.label}: ${node.detail || node.kind}`; render();
      });
      group.appendChild(g);
    });
    svg.appendChild(group);
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#64748b"/></marker>';
    svg.prepend(defs);
  }

  svg.onpointermove = event => {
    if (!dragging) return;
    const next = point(event); dragging.node.x += next.x - dragging.offset.x; dragging.node.y += next.y - dragging.offset.y; dragging.offset = next;
    emitPositions(); render();
  };
  svg.onpointerup = () => { dragging = null; };
  svg.onwheel = event => { event.preventDefault(); scale = Math.max(.55, Math.min(1.8, scale * (event.deltaY > 0 ? .92 : 1.08))); render(); };
  svg.onpointerdown = () => { selectedId = null; selected.textContent = 'Select a node'; render(); };
  reset.onclick = resetLayout;
  render();
}
"""

_INTERACTIVE_GRAPH = st.components.v2.component(
    "prism_interactive_scenario_graph",
    html=_GRAPH_HTML,
    css=_GRAPH_CSS,
    js=_GRAPH_JS,
)


def interactive_scenario_graph(
    graph_data: dict[str, Any],
    positions: dict[str, dict[str, float]] | None = None,
    *,
    key: str = "prism_scenario_graph",
):
    return _INTERACTIVE_GRAPH(
        data={**graph_data, "positions": positions or {}},
        key=key,
        width="stretch",
        height=620,
        on_positions_change=lambda: None,
    )


def graph_data_from_result(result) -> dict[str, list[dict[str, Any]]]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    if result.policy_graph:
        for name, attrs in result.policy_graph.nodes(data=True):
            node_id = f"policy:{name}"
            nodes[node_id] = {"id": node_id, "label": str(name)[:20], "kind": "topic", "detail": attrs.get("node_type", "Concept"), "color": "#fde68a" if attrs.get("node_type") == "Policy" else "#fecdd3" if attrs.get("node_type") == "Risk" else "#dbeafe"}
        for source, target, attrs in result.policy_graph.edges(data=True):
            edges.append({"source": f"policy:{source}", "target": f"policy:{target}", "label": attrs.get("relation", "RELATED"), "kind": "semantic"})
    if result.graph:
        for name, attrs in result.graph.nodes(data=True):
            obj = attrs.get("obj")
            detail = attrs.get("role", attrs.get("agent_type", "agent"))
            if obj:
                detail = f"{detail} · S{obj.metrics.stress} T{obj.metrics.trust}"
            node_id = f"agent:{name}"
            nodes[node_id] = {"id": node_id, "label": str(name)[:20], "kind": "agent", "detail": detail, "color": "#bbf7d0" if attrs.get("agent_type") == "internal" else "#fed7aa"}
        for source, target, attrs in result.graph.edges(data=True):
            edges.append({"source": f"agent:{source}", "target": f"agent:{target}", "label": attrs.get("relation", "CONNECTED"), "kind": "topology"})
    for message in result.messages:
        edges.append({"source": f"agent:{message.sender}", "target": f"agent:{message.receiver}", "label": message.sentiment.upper(), "kind": "message"})
    return {"nodes": list(nodes.values()), "edges": edges}
