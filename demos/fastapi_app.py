"""
FastAPI web application for LIGHTNING demo.
Replacement for Streamlit with better performance and reliability.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Import LIGHTNING components
from lightning import check
from lightning.models import Decision

# Resolve paths relative to this file so the app can be launched from any cwd
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI app
app = FastAPI(title="LIGHTNING Demo", description="Neurosymbolic Safety Layer for Autonomous Research")

# Setup templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Request models
class AnalysisRequest(BaseModel):
    protocol_text: str
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

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main demo page."""
    return templates.TemplateResponse(request, "index.html")

@app.get("/adversarial", response_class=HTMLResponse)
async def adversarial_demo(request: Request):
    """Adversarial robustness testing page."""
    return templates.TemplateResponse(request, "adversarial.html")

@app.get("/audit", response_class=HTMLResponse)
async def audit_dashboard(request: Request):
    """Audit dashboard page."""
    return templates.TemplateResponse(request, "audit.html")

@app.get("/visualization", response_class=HTMLResponse)
async def visualization_page(request: Request):
    """Graph visualization page."""
    return templates.TemplateResponse(request, "visualization.html")

# API Endpoints
@app.post("/api/analyze")
async def analyze_protocol(request: AnalysisRequest):
    """Main LIGHTNING analysis endpoint."""
    try:
        result = check(
            request.protocol_text,
            enable_audit=request.enable_audit,
            audit_context=request.context
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
            "audit_id": getattr(result, 'audit_id', None)
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

        # Re-analyze the modified protocol
        recheck_result = check(modified_protocol)

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
        result = check(protocol_text, audit_context={"source": "chemcrow"})

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

if __name__ == "__main__":
    print("🛡️ Starting LIGHTNING FastAPI Demo Server...")
    print("📱 Main Demo: http://localhost:8000")
    print("🧪 Adversarial Test: http://localhost:8000/adversarial")
    print("🔍 Audit Dashboard: http://localhost:8000/audit")
    print("🕸️ Visualization: http://localhost:8000/visualization")
    print("📚 API Docs: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )