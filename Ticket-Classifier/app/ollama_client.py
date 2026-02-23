import json
import re
import httpx


def generate_classification(ticket: dict, categories, model: str, api_url: str) -> dict:
    prompt = build_prompt(ticket, categories)
    payload = {"model": model, "prompt": prompt, "stream": False, "temperature": 0}
    try:
        r = httpx.post(api_url, json=payload, timeout=60.0)
        r.raise_for_status()
        text = r.text.strip()
        lines = text.split('\n')
        
        if len(lines) > 1:
            final_response = None
            for line in reversed(lines):
                if line.strip():
                    try:
                        obj = json.loads(line)
                        if obj.get("done", False):
                            final_response = obj.get("response", "")
                            break
                    except Exception:
                        pass
            if final_response is not None:
                text = final_response
            else:
                try:
                    last_obj = json.loads(lines[-1].strip())
                    text = last_obj.get("response", text)
                except Exception:
                    pass
        else:
            try:
                obj = json.loads(text)
                text = obj.get("response", "") or obj.get("text", "") or text
            except Exception:
                pass
                
    except Exception as e:
        err_text = str(e)
        raw = r.text if 'r' in locals() and getattr(r, 'text', None) else ""
        text = f"ERROR: {err_text}\n{raw}"

    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        last = text.strip().splitlines()[-1] if text.strip() else ""
        try:
            return json.loads(last)
        except Exception:
            return {"category": "Other / Needs Review", "confidence": 0.0, "queue": "triage", "reason": text.strip() or "model-unreachable-or-invalid-response", "human_review": True}

    try:
        data = json.loads(m.group(0))
        return data
    except Exception:
        return {"category": "Other / Needs Review", "confidence": 0.0, "queue": "triage", "reason": text.strip() or "model-unreachable-or-invalid-response", "human_review": True}


def build_prompt(ticket: dict, categories) -> str:
    cat_list = "; ".join(categories)
    prompt = (
        "You are a ticket classification assistant.\n"
        "Given the ticket fields, return STRICT JSON with keys: category, confidence (0-1), queue, reason, human_review.\n"
        "Only output valid JSON and nothing else.\n\n"
        f"Categories: {cat_list}\n\n"
        "Example:\n"
        "Ticket: subject='Payment failed', description='My credit card was declined while paying invoice', source_channel='email', customer_type='paid'\n"
        "Output: {\n  \"category\": \"Billing & Payments\",\n  \"confidence\": 0.95,\n  \"queue\": \"billing-queue\",\n  \"reason\": \"Payment failure language and billing keywords\",\n  \"human_review\": false\n}\n\n"
        "Now classify this ticket:\n"
        f"Ticket: subject={json.dumps(ticket.get('subject',''))}, description={json.dumps(ticket.get('description',''))}, source_channel={json.dumps(ticket.get('source_channel',''))}, customer_type={json.dumps(ticket.get('customer_type',''))}, language={json.dumps(ticket.get('language',''))}\n"
    )
    return prompt
