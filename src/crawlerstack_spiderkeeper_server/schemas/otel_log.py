"""Otel log Record schema"""

from opentelemetry._logs import SeverityNumber  # noqa
from pydantic import BaseModel


class LogRecordSchema(BaseModel):
    """Log record schema"""
    timestamp: int = 0
    trace_id: int = 0
    span_id: int = 0
    trace_flags: bool = False
    severity_number: SeverityNumber = SeverityNumber.INFO
    body: str | int | dict | None = None
    attributes: dict = None
