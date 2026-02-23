import json
from datetime import datetime
from pathlib import Path


AUDIT_LOG_DIR = Path(__file__).resolve().parents[1] / "audit_logs"


def ensure_audit_dir():
    AUDIT_LOG_DIR.mkdir(exist_ok=True)


def log_classification(ticket: dict, result: dict, overrides: dict = None) -> str:
    ensure_audit_dir()
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "ticket": ticket,
        "classification": result,
        "overrides": overrides or {},
    }
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = AUDIT_LOG_DIR / f"classifications-{today}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return log_file.name


def read_audit_logs(limit: int = 100) -> list:
    ensure_audit_dir()
    entries = []
    log_files = sorted(AUDIT_LOG_DIR.glob("classifications-*.jsonl"), reverse=True)
    for log_file in log_files:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                        if len(entries) >= limit:
                            return entries[:limit]
                    except json.JSONDecodeError:
                        pass
    return entries


def get_low_confidence_tickets(threshold: float = 0.65, limit: int = 50) -> list:
    all_entries = read_audit_logs(limit=1000)
    low_conf = [e for e in all_entries if e.get("classification", {}).get("confidence", 1.0) < threshold]
    return low_conf[:limit]
