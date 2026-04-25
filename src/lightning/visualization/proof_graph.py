"""
Convert ProofTree to interactive graph visualization.
"""
from lightning.models import ProofTree
import json
from typing import Dict, List, Any


def proof_tree_to_graph(proof_tree: ProofTree) -> Dict[str, Any]:
    """
    Convert ProofTree to D3.js-compatible graph structure.

    Returns:
        Dictionary with 'nodes' and 'links' arrays for D3 visualization.
    """
    nodes = []
    links = []
    node_id_counter = 0

    # Map element names to node IDs for link creation
    element_to_node_id = {}

    # Create nodes for controlled elements (outcomes)
    for element in proof_tree.controlled_elements:
        node_id = f"element_{node_id_counter}"
        nodes.append({
            "id": node_id,
            "label": element,
            "type": "controlled_element",
            "group": "outcome",
            "color": "#ff4444",
            "size": 20
        })
        element_to_node_id[element] = node_id
        node_id_counter += 1

    # Create nodes for each proof step (rules)
    for i, step in enumerate(proof_tree.steps):
        rule_node_id = f"rule_{i}"
        nodes.append({
            "id": rule_node_id,
            "label": step.rule_name.replace("_", " ").title(),
            "type": "rule",
            "group": "reasoning",
            "color": "#4444ff",
            "size": 15,
            "conclusion": step.conclusion
        })

        # Create nodes for premises (if not already exist)
        premise_node_ids = []
        for j, premise in enumerate(step.premises[:3]):  # Limit for readability
            premise_node_id = f"premise_{i}_{j}"
            premise_label = premise[:30] + "..." if len(premise) > 30 else premise

            nodes.append({
                "id": premise_node_id,
                "label": premise_label,
                "type": "premise",
                "group": "facts",
                "color": "#44aa44",
                "size": 10,
                "full_text": premise
            })
            premise_node_ids.append(premise_node_id)

        # Create links: premises -> rule
        for premise_id in premise_node_ids:
            links.append({
                "source": premise_id,
                "target": rule_node_id,
                "type": "supports",
                "label": "supports"
            })

        # Create link: rule -> controlled element (if this rule leads to one)
        conclusion_element = None
        for element in proof_tree.controlled_elements:
            if element in step.conclusion:
                conclusion_element = element
                break

        if conclusion_element and conclusion_element in element_to_node_id:
            links.append({
                "source": rule_node_id,
                "target": element_to_node_id[conclusion_element],
                "type": "concludes",
                "label": "concludes"
            })

    # Add cross-regime links if available
    if hasattr(proof_tree, 'cross_regime_links'):
        for link in proof_tree.cross_regime_links:
            # Find nodes for linked elements
            source_node = next((n for n in nodes if link.element in n["label"]), None)
            if source_node:
                # Create cross-regime link node
                cross_link_id = f"cross_regime_{len(nodes)}"
                nodes.append({
                    "id": cross_link_id,
                    "label": f"Cross-regime:\n{link.explanation}",
                    "type": "cross_regime",
                    "group": "meta",
                    "color": "#aa44aa",
                    "size": 12
                })

                links.append({
                    "source": source_node["id"],
                    "target": cross_link_id,
                    "type": "cross_regime",
                    "label": link.link_type
                })

    return {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "controlled_elements": len(proof_tree.controlled_elements),
            "proof_steps": len(proof_tree.steps)
        }
    }


def generate_d3_html(graph_data: Dict[str, Any]) -> str:
    """Generate standalone HTML with D3.js visualization."""

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AEGIS Proof Tree Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            .node {{ cursor: pointer; }}
            .link {{ stroke: #999; stroke-opacity: 0.6; }}
            .node text {{ font: 10px sans-serif; pointer-events: none; text-anchor: middle; }}
            .tooltip {{ position: absolute; background: rgba(0,0,0,0.8); color: white;
                       padding: 8px; border-radius: 4px; font-size: 12px; max-width: 200px; }}
            #graph-container {{ width: 100%; height: 600px; border: 1px solid #ccc; }}
            #controls {{ margin-bottom: 10px; }}
            #info {{ margin-top: 10px; font-size: 14px; }}
            .legend {{ position: absolute; top: 10px; right: 10px; background: white;
                      padding: 10px; border: 1px solid #ccc; border-radius: 4px; }}
            .legend-item {{ margin: 5px 0; }}
            .legend-color {{ width: 15px; height: 15px; display: inline-block; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <h2>🛡️ AEGIS Proof Tree Visualization</h2>
        <div id="controls">
            <button onclick="resetZoom()">Reset View</button>
            <button onclick="pauseSimulation()">Pause Physics</button>
            <button onclick="resumeSimulation()">Resume Physics</button>
        </div>
        <div id="graph-container">
            <div class="legend">
                <div class="legend-item"><span class="legend-color" style="background: #ff4444;"></span>Controlled Elements</div>
                <div class="legend-item"><span class="legend-color" style="background: #4444ff;"></span>Rules</div>
                <div class="legend-item"><span class="legend-color" style="background: #44aa44;"></span>Facts/Premises</div>
                <div class="legend-item"><span class="legend-color" style="background: #aa44aa;"></span>Cross-regime Links</div>
            </div>
        </div>
        <div id="info">
            <p><strong>Nodes:</strong> {total_nodes} | <strong>Links:</strong> {total_links} |
            <strong>Controlled Elements:</strong> {controlled_elements} | <strong>Proof Steps:</strong> {proof_steps}</p>
        </div>

        <script>
            const graphData = {graph_json};

            const width = 800;
            const height = 600;

            const svg = d3.select("#graph-container")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            // Add zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.5, 3])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});

            svg.call(zoom);

            const g = svg.append("g");

            const simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(d => d.size + 5));

            // Create links
            const link = g.append("g")
                .selectAll("line")
                .data(graphData.links)
                .enter().append("line")
                .attr("class", "link")
                .attr("stroke-width", 2)
                .attr("stroke", d => {{
                    if (d.type === "cross_regime") return "#aa44aa";
                    if (d.type === "concludes") return "#ff6666";
                    return "#999";
                }});

            // Create nodes
            const node = g.append("g")
                .selectAll("circle")
                .data(graphData.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", d => d.size || 10)
                .attr("fill", d => d.color)
                .attr("stroke", "#fff")
                .attr("stroke-width", 2)
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            // Add labels
            const label = g.append("g")
                .selectAll("text")
                .data(graphData.nodes)
                .enter().append("text")
                .text(d => d.label.split("\\n")[0]) // Only first line for labels
                .attr("font-size", 10)
                .attr("text-anchor", "middle")
                .attr("dy", 3)
                .attr("fill", "white")
                .attr("font-weight", "bold")
                .style("pointer-events", "none");

            // Tooltip
            const tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            node.on("mouseover", function(event, d) {{
                tooltip.transition().duration(200).style("opacity", 0.9);
                let content = `<strong>${{d.label}}</strong><br/>Type: ${{d.type}}`;
                if (d.conclusion) content += `<br/>Conclusion: ${{d.conclusion}}`;
                if (d.full_text) content += `<br/>Details: ${{d.full_text}}`;
                tooltip.html(content)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
            }})
            .on("mouseout", function(d) {{
                tooltip.transition().duration(500).style("opacity", 0);
            }})
            .on("click", function(event, d) {{
                // Center on clicked node
                const transform = d3.zoomTransform(svg.node());
                const newTransform = transform
                    .translate(width / 2 - d.x, height / 2 - d.y)
                    .scale(1.5);
                svg.transition().duration(750).call(zoom.transform, newTransform);
            }});

            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);

                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            }});

            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}

            // Control functions
            function resetZoom() {{
                svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
            }}

            function pauseSimulation() {{
                simulation.stop();
            }}

            function resumeSimulation() {{
                simulation.restart();
            }}

            // Auto-fit to content
            setTimeout(() => {{
                const bounds = g.node().getBBox();
                const fullWidth = bounds.width;
                const fullHeight = bounds.height;
                const midX = bounds.x + fullWidth / 2;
                const midY = bounds.y + fullHeight / 2;
                const scale = 0.8 / Math.max(fullWidth / width, fullHeight / height);
                const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

                svg.call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
            }}, 1000);
        </script>
    </body>
    </html>
    """

    return html_template.format(
        graph_json=json.dumps(graph_data),
        total_nodes=graph_data["metadata"]["total_nodes"],
        total_links=graph_data["metadata"]["total_links"],
        controlled_elements=graph_data["metadata"]["controlled_elements"],
        proof_steps=graph_data["metadata"]["proof_steps"]
    )


def create_streamlit_graph_component(graph_data: Dict[str, Any]) -> str:
    """Create a Streamlit-compatible graph component."""
    # Simplified version for Streamlit embedding
    streamlit_html = f"""
    <div id="aegis-graph" style="width: 100%; height: 500px; border: 1px solid #ccc;"></div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        const data = {json.dumps(graph_data)};

        // Simplified D3 graph for Streamlit
        const width = 600;
        const height = 400;

        const svg = d3.select("#aegis-graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("stroke", "#999")
            .attr("stroke-width", 1.5);

        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("r", d => d.size / 2)
            .attr("fill", d => d.color);

        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .text(d => d.label.substring(0, 15))
            .attr("font-size", 8)
            .attr("text-anchor", "middle");

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y + 3);
        }});
    </script>
    """

    return streamlit_html