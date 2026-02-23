from pydantic import BaseModel
from typing import Optional, List


class Ticket(BaseModel):
    subject: Optional[str] = ""
    description: Optional[str] = ""
    source_channel: Optional[str] = ""
    customer_type: Optional[str] = ""
    language: Optional[str] = "en"


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    queue: str
    reason: str
    human_review: bool


class BatchClassificationRequest(BaseModel):
    tickets: List[Ticket]


class BatchClassificationResponse(BaseModel):
    results: List[ClassificationResponse]
    total: int
    processing_time_ms: float
