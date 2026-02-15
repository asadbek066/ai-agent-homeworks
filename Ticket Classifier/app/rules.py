import yaml
from pathlib import Path


class RulesEngine:
    def __init__(self, config_path: str):
        self.path = Path(config_path)
        self.reload()

    def reload(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

    def apply(self, ticket: dict, model_out: dict) -> dict:
        rules = self.cfg.get("rules", {})
        forced = set(rules.get("forced_human_review_categories", []))
        threshold = float(rules.get("confidence_threshold", 0.65))
        enterprise_boost = float(rules.get("enterprise_confidence_boost", 0.0))

        category = model_out.get("category")
        confidence = float(model_out.get("confidence", 0.0))
        if ticket.get("customer_type", "").lower() == "enterprise":
            confidence += enterprise_boost

        human_review = bool(model_out.get("human_review", False))
        if category in forced or confidence < threshold:
            human_review = True

        model_out["confidence"] = min(max(confidence, 0.0), 1.0)
        model_out["human_review"] = human_review
        model_out["queue"] = model_out.get("queue") or self.cfg.get("queue_map", {}).get(category, "triage")
        return model_out
