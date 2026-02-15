from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from app.schemas import Ticket, ClassificationResponse, BatchClassificationRequest, BatchClassificationResponse
from app.ollama_client import generate_classification
from app.rules import RulesEngine
from app.audit import log_classification, read_audit_logs, get_low_confidence_tickets
import httpx
import yaml
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"

app = FastAPI(title="Ticket Classifier")
rules = RulesEngine(str(CONFIG_PATH))


@app.get("/")
def admin_dashboard():
    admin_file = ROOT / "app" / "admin.html"
    if admin_file.exists():
        return FileResponse(admin_file, media_type="text/html")
    return {"message": "Admin dashboard - visit http://localhost:8000/ to view"}


@app.get("/test")
def test_page():
    test_file = ROOT / "app" / "test.html"
    if test_file.exists():
        return FileResponse(test_file, media_type="text/html")
    return {"message": "Test page not found"}


@app.post("/classify", response_model=ClassificationResponse)
async def classify(ticket: Ticket):
    try:
        cfg = yaml.safe_load(open(CONFIG_PATH, "r", encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config load error: {e}")

    categories = cfg.get("categories", [])
    ollama_cfg = cfg.get("ollama", {})
    model = ollama_cfg.get("model", "deepseek-r1:1.5b")
    api_url = ollama_cfg.get("api_url", "http://localhost:11434/api/generate")

    model_out = generate_classification(ticket.dict(), categories, model, api_url)
    if not isinstance(model_out, dict):
        raise HTTPException(status_code=500, detail="Model returned invalid output")

    result = rules.apply(ticket.dict(), model_out)
    resp = {
        "category": result.get("category", "Other / Needs Review"),
        "confidence": float(result.get("confidence", 0.0)),
        "queue": result.get("queue", "triage"),
        "reason": result.get("reason", ""),
        "human_review": bool(result.get("human_review", True)),
    }
    log_classification(ticket.dict(), resp)

    return ClassificationResponse(**resp)


@app.post("/reload-config")
def reload_config():
    try:
        rules.reload()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verify-ollama-connection")
def verify_ollama():
    try:
        cfg = yaml.safe_load(open(CONFIG_PATH, "r", encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config load error: {e}")

    ollama_cfg = cfg.get("ollama", {})
    model = ollama_cfg.get("model", "deepseek-r1:1.5b")
    api_url = ollama_cfg.get("api_url", "http://localhost:11434/api/generate")

    payload = {"model": model, "prompt": "test", "stream": False}
    try:
        r = httpx.post(api_url, json=payload, timeout=10.0)
        if r.status_code == 200:
            return {"connected": True, "model": model, "api_url": api_url, "status": "OK"}
        else:
            return {"connected": False, "status_code": r.status_code, "api_url": api_url, "error": r.text[:200]}
    except Exception as e:
        return {
            "connected": False,
            "api_url": api_url,
            "model": model,
            "error": str(e),
            "hint": "Is Ollama running? Check: (1) Start Ollama desktop app, (2) Or run 'ollama serve' in a terminal, (3) Check if api_url in config.yaml is correct."
        }


@app.post("/classify-batch", response_model=BatchClassificationResponse)
async def classify_batch(req: BatchClassificationRequest):
    start = time.time()
    results = []
    
    for ticket in req.tickets:
        try:
            cfg = yaml.safe_load(open(CONFIG_PATH, "r", encoding="utf-8"))
            categories = cfg.get("categories", [])
            ollama_cfg = cfg.get("ollama", {})
            model = ollama_cfg.get("model", "deepseek-r1:1.5b")
            api_url = ollama_cfg.get("api_url", "http://localhost:11434/api/generate")
            
            model_out = generate_classification(ticket.dict(), categories, model, api_url)
            result = rules.apply(ticket.dict(), model_out)
            
            resp = {
                "category": result.get("category", "Other / Needs Review"),
                "confidence": float(result.get("confidence", 0.0)),
                "queue": result.get("queue", "triage"),
                "reason": result.get("reason", ""),
                "human_review": bool(result.get("human_review", True)),
            }
            results.append(ClassificationResponse(**resp))
            log_classification(ticket.dict(), resp)
        except Exception as e:
            results.append(ClassificationResponse(
                category="Other / Needs Review",
                confidence=0.0,
                queue="triage",
                reason=str(e),
                human_review=True
            ))
    
    elapsed_ms = (time.time() - start) * 1000
    return BatchClassificationResponse(results=results, total=len(results), processing_time_ms=elapsed_ms)


@app.get("/audit-logs")
def get_audit_logs(limit: int = 100):
    try:
        logs = read_audit_logs(limit=limit)
        return {"total": len(logs), "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/low-confidence-tickets")
def get_low_confidence(threshold: float = 0.65, limit: int = 50):
    try:
        tickets = get_low_confidence_tickets(threshold=threshold, limit=limit)
        return {"threshold": threshold, "count": len(tickets), "tickets": tickets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
