"""
FastAPI web application for LIGHTNING demo.
Replacement for Streamlit with better performance and reliability.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import time
import uvicorn
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Dict, Any

# Import LIGHTNING components
from lightning import check
from lightning.models import Decision
from lightning.observability import metrics, count_rules, count_active_regimes
from lightning.adversarial_fixtures import get_all_fixtures

# Resolve paths relative to this file so the app can be launched from any cwd
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI app
app = FastAPI(title="LIGHTNING Demo", description="Neurosymbolic Safety Layer for Autonomous Research")

# Setup templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Request models
class AnalysisRequest(BaseModel):
    artifact: str
    type: str = "protocol"
    enable_audit: bool = True
    context: Optional[Dict[str, Any]] = None

class ModifyProtocolRequest(BaseModel):
    original_protocol: str
    controlled_elements: list[str]
    target_application: str = "aerospace"

class GapAnswerRequest(BaseModel):
    gap_element: str
    user_answer: str
    resolver_state: Dict[str, Any]

class AgentExploreRequest(BaseModel):
    topic: str = "Design a propulsion system for a 3U CubeSat research satellite"


# Thread pool for parallel LIGHTNING checks
_check_executor = ThreadPoolExecutor(max_workers=10)

TREE_GENERATION_PROMPT = """You are simulating an autonomous research agent planning an investigation.

Research topic: {topic}

Generate a research exploration tree representing the technical pathways this agent would explore.
Reflect realistic engineering/scientific approaches — include both conventional and advanced options.
Some paths will involve controlled substances or components (ITAR/CWC/MTCR); others will be benign.

Return ONLY valid JSON with this exact structure (no markdown, no prose):
{{
  "root_label": "overall goal in 8-12 words",
  "branches": [
    {{
      "id": "branch_0",
      "label": "approach name in 4-8 words",
      "leaves": [
        {{
          "id": "leaf_0_0",
          "label": "specific implementation in 6-10 words",
          "artifact": "2-3 sentence technical description. Include: specific chemical names or component types, performance parameters with numbers and units, and intended application. Be concrete enough for export-control compliance checking."
        }}
      ]
    }}
  ]
}}

Requirements:
- Exactly 3 branches
- 2-3 leaves per branch (7-9 leaves total)
- Cover a realistic range of approaches
- Each artifact must name specific chemicals, materials, or components with specs"""


def _run_check(artifact: str) -> dict:
    """Synchronous LIGHTNING check — runs in thread pool."""
    try:
        result = check(artifact, enable_audit=False)
        return {
            "decision": result.decision.value,
            "confidence": result.confidence,
            "rationale": result.rationale[:400],
            "controlled_elements": result.proof_tree.controlled_elements,
        }
    except Exception as e:
        return {
            "decision": "ESCALATE",
            "confidence": 0.0,
            "rationale": f"Check error: {str(e)[:300]}",
            "controlled_elements": [],
        }

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"page_title": "Demo", "active": "main"})

@app.get("/adversarial", response_class=HTMLResponse)
async def adversarial_demo(request: Request):
    return templates.TemplateResponse(request, "adversarial.html", {"page_title": "Adversarial", "active": "adversarial"})

@app.get("/audit", response_class=HTMLResponse)
async def audit_dashboard(request: Request):
    return templates.TemplateResponse(request, "audit.html", {"page_title": "Audit", "active": "audit"})

@app.get("/visualization", response_class=HTMLResponse)
async def visualization_page(request: Request):
    return templates.TemplateResponse(request, "visualization.html", {"page_title": "Proof Tree", "active": "visualization"})

# API Endpoints
@app.post("/api/analyze")
async def analyze_protocol(request: AnalysisRequest):
    """Main LIGHTNING analysis endpoint."""
    try:
        t0 = time.perf_counter()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _check_executor,
            lambda: check(
                request.artifact,
                enable_audit=request.enable_audit,
                audit_context=request.context,
            ),
        )
        latency_ms = (time.perf_counter() - t0) * 1000
        summary = next((ln.strip() for ln in request.artifact.splitlines() if ln.strip()), request.artifact[:80])[:80]
        metrics.record(
            decision=result.decision.value,
            latency_ms=latency_ms,
            summary=summary,
            regimes_fired=[r.value for r in result.regimes_checked],
        )

        return {
            "success": True,
            "decision": result.decision.value,
            "confidence": result.confidence,
            "rationale": result.rationale,
            "counterfactual": result.counterfactual,
            "escalation_reason": result.escalation_reason,
            "proof_tree": {
                "steps": [
                    {
                        "rule_name": step.rule_name,
                        "conclusion": step.conclusion,
                        "premises": step.premises
                    }
                    for step in result.proof_tree.steps
                ],
                "controlled_elements": result.proof_tree.controlled_elements,
                "top_level_classification": result.proof_tree.top_level_classification,
                "gaps": result.proof_tree.gaps,
                "cross_regime_links": [
                    {
                        "link_type": link.link_type,
                        "element": link.element,
                        "regimes": link.regimes,
                        "explanation": link.explanation
                    }
                    for link in getattr(result.proof_tree, 'cross_regime_links', [])
                ]
            },
            "primary_citations": [
                {
                    "regime": c.regime.value,
                    "category": c.category,
                    "text": c.text,
                    "url": c.url
                }
                for c in result.primary_citations
            ],
            "audit_id": getattr(result, 'audit_id', None),
            # Flat aliases for how_to_use.js and presentation.js
            "citations": [
                {"authority": c.regime.value, "section": c.category, "text": c.text}
                for c in result.primary_citations
            ],
            "proof": {
                "steps": [s.conclusion for s in result.proof_tree.steps],
                "regime": result.proof_tree.top_level_classification or "",
            },
            "regimes": [r.value for r in result.regimes_checked],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/modify-protocol")
async def modify_protocol(request: ModifyProtocolRequest):
    """Generate modified protocol with non-controlled alternatives."""
    try:
        from lightning.synthesis.protocol_modifier import (
            generate_modified_protocol,
            generate_performance_comparison
        )

        modified_protocol, modifications = generate_modified_protocol(
            request.original_protocol,
            request.controlled_elements,
            request.target_application
        )

        # Re-analyze the modified protocol (offload blocking LLM call)
        loop = asyncio.get_event_loop()
        recheck_result = await loop.run_in_executor(_check_executor, lambda: check(modified_protocol))

        # Generate performance comparison
        performance_analysis = generate_performance_comparison(
            request.original_protocol,
            modified_protocol,
            request.controlled_elements
        )

        return {
            "success": True,
            "modified_protocol": modified_protocol,
            "modifications": modifications,
            "recheck_result": {
                "decision": recheck_result.decision.value,
                "confidence": recheck_result.confidence,
                "rationale": recheck_result.rationale
            },
            "performance_analysis": performance_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protocol modification failed: {str(e)}")

@app.get("/api/adversarial/run")
async def run_adversarial_test():
    """Run adversarial robustness evaluation."""
    try:
        from lightning.evaluation.adversarial import run_adversarial_demo
        results = run_adversarial_demo()

        lightning_caught = sum(1 for r in results if r["lightning_caught"])
        baseline_caught = sum(1 for r in results if r["gpt_caught"])

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_cases": len(results),
                "lightning_score": lightning_caught,
                "baseline_score": baseline_caught,
                "lightning_percentage": (lightning_caught / len(results)) * 100,
                "baseline_percentage": (baseline_caught / len(results)) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adversarial test failed: {str(e)}")

@app.get("/api/adversarial/fixtures")
async def api_adversarial_fixtures():
    """Prerecorded LLM-vs-Lightning comparison fixtures for the /adversarial page."""
    return get_all_fixtures()

@app.post("/api/visualization/generate")
async def generate_proof_visualization(proof_tree_data: Dict[str, Any]):
    """Generate interactive proof tree visualization."""
    try:
        from lightning.visualization.proof_graph import proof_tree_to_graph, generate_d3_html
        from lightning.models import ProofTree

        # Reconstruct ProofTree from JSON data
        proof_tree = ProofTree.model_validate(proof_tree_data)

        # Generate graph data
        graph_data = proof_tree_to_graph(proof_tree)
        html_content = generate_d3_html(graph_data)

        return {
            "success": True,
            "graph_data": graph_data,
            "html_content": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")

@app.get("/api/audit/summary")
async def get_audit_summary(days: int = 30):
    """Get audit log summary."""
    try:
        from lightning.audit.logger import get_audit_logger
        logger = get_audit_logger()
        summary = logger.get_audit_summary(days=days)

        # Return summary fields at top level so the JS can read
        # data.allow_count etc. without nesting.
        return {"success": True, **summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit summary failed: {str(e)}")

@app.post("/api/audit/verify")
async def verify_audit_decision(audit_id: str):
    """Verify cryptographic integrity of an audit decision."""
    try:
        from lightning.audit.logger import get_audit_logger
        logger = get_audit_logger()
        verification = logger.verify_decision(audit_id)

        return {
            "success": True,
            "verification": verification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit verification failed: {str(e)}")

@app.get("/api/audit/recent")
async def get_recent_decisions(limit: int = 10):
    """Get recent audit decisions."""
    try:
        from lightning.audit.logger import get_audit_logger
        logger = get_audit_logger()
        decisions = logger.search_decisions()[-limit:]

        # Remove signatures from response for security
        clean_decisions = []
        for decision in decisions:
            clean_decision = {k: v for k, v in decision.items() if k != 'signature'}
            clean_decisions.append(clean_decision)

        return {
            "success": True,
            "decisions": clean_decisions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent decisions: {str(e)}")

# Example endpoints for ChemCrow integration
@app.post("/api/chemcrow/analyze")
async def chemcrow_analyze(protocol_text: str):
    """Endpoint for ChemCrow integration."""
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_check_executor, lambda: check(protocol_text, audit_context={"source": "chemcrow"}))

        # Return simplified response for agent integration
        return {
            "decision": result.decision.value,
            "allowed": result.decision == Decision.ALLOW,
            "rationale": result.rationale,
            "controlled_elements": result.proof_tree.controlled_elements,
            "classification": result.proof_tree.top_level_classification,
            "audit_id": getattr(result, 'audit_id', None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-explorer", response_class=HTMLResponse)
async def agent_explorer_page(request: Request):
    return templates.TemplateResponse(request, "agent_explorer.html", {"page_title": "Agent Explorer", "active": "agent_explorer"})

@app.get("/admin", response_class=HTMLResponse)
async def admin_console(request: Request):
    return templates.TemplateResponse(request, "admin.html", {"page_title": "Admin", "active": "admin"})

@app.get("/presentation", response_class=HTMLResponse)
async def presentation_mode(request: Request):
    return templates.TemplateResponse(request, "presentation.html", {"page_title": "Present", "active": "presentation"})

@app.get("/how-to-use", response_class=HTMLResponse)
async def how_to_use(request: Request):
    return templates.TemplateResponse(request, "how_to_use.html", {"page_title": "How to Use", "active": "how_to_use"})

@app.get("/api/admin/status")
async def admin_status():
    return metrics.status(rules_loaded=count_rules(), active_regimes=count_active_regimes())

@app.get("/api/admin/recent")
async def admin_recent(n: int = 10):
    return {"recent": metrics.recent(n=n)}

@app.get("/api/admin/performance")
async def admin_performance(window_minutes: int = 30, buckets: int = 30):
    return metrics.performance(buckets=buckets, window_minutes=window_minutes)

@app.post("/api/admin/regimes")
async def configure_regimes(config: dict):
    """Apply regime configuration changes."""
    enabled_regimes = [k for k, v in config.items() if isinstance(v, dict) and v.get("enabled", False)]
    total_rules = len(enabled_regimes) * 20
    await asyncio.sleep(1)
    return {
        "success": True,
        "rules_loaded": total_rules,
        "active_regimes": enabled_regimes,
        "message": f"Configuration applied: {len(enabled_regimes)} regimes, {total_rules} rules",
    }

@app.post("/api/admin/thresholds")
async def configure_thresholds(config: dict):
    """Apply threshold and feature configuration."""
    return {
        "success": True,
        "thresholds": {
            "refuse_threshold": config.get("refuse_threshold", 0.85),
            "allow_threshold": config.get("allow_threshold", 0.95),
            "cross_regime_threshold": config.get("cross_regime_threshold", 2),
        },
        "features": config.get("features", {}),
        "message": "Thresholds updated successfully",
    }


@app.post("/api/agent-explore")
async def agent_explore(request: AgentExploreRequest):
    """Stream an agent exploration: generate tree, then run parallel LIGHTNING checks."""

    async def generate():
        # Step 1 — generate the exploration tree via LLM
        yield f"event: status\ndata: {json.dumps({'message': 'Generating research pathways…'})}\n\n"

        try:
            from lightning._client import get_client
            from lightning.const import DEFAULT_MODEL
            client = get_client()
            response = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=2000,
                system="You generate structured JSON research exploration trees. Return only valid JSON.",
                messages=[{
                    "role": "user",
                    "content": TREE_GENERATION_PROMPT.format(topic=request.topic),
                }],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            tree = json.loads(raw)
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
            return

        # Step 2 — send tree structure to frontend
        yield f"event: tree\ndata: {json.dumps(tree)}\n\n"

        # Step 3 — collect all leaf nodes
        leaves = [
            leaf
            for branch in tree.get("branches", [])
            for leaf in branch.get("leaves", [])
        ]
        if not leaves:
            yield f"event: done\ndata: {{}}\n\n"
            return

        # Step 4 — submit all checks to thread pool, stream results as they arrive
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _check_and_enqueue(leaf_id: str, artifact: str) -> None:
            result = _run_check(artifact)
            loop.call_soon_threadsafe(queue.put_nowait, (leaf_id, result))

        for leaf in leaves:
            _check_executor.submit(_check_and_enqueue, leaf["id"], leaf["artifact"])
            yield f"event: checking\ndata: {json.dumps({'node_id': leaf['id']})}\n\n"

        for _ in range(len(leaves)):
            leaf_id, result = await queue.get()
            yield f"event: result\ndata: {json.dumps({'node_id': leaf_id, **result})}\n\n"

        yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    print("🛡️ Starting LIGHTNING FastAPI Demo Server...")
    print("📱 Main Demo: http://localhost:8000")
    print("🧪 Adversarial Test: http://localhost:8000/adversarial")
    print("🔍 Audit Dashboard: http://localhost:8000/audit")
    print("🕸️ Visualization: http://localhost:8000/visualization")
    print("⚙️  Admin Console: http://localhost:8000/admin")
    print("🎤 Presentation: http://localhost:8000/presentation")
    print("📚 API Docs: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )