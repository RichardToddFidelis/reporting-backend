# reporting-backend/api/schemas/job.py
from ninja import Schema
from pydantic.types import Literal
from pydantic import field_validator
from typing import List, Optional


class JobSchemaIn(Schema):
    report_id: int
    report_modifier_id: Optional[int] = None
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"] = "PENDING"

    @field_validator("report_id")
    @classmethod
    def validate_report_id(cls, value: int) -> int:
        from api.models.report import Report

        if not Report.objects.filter(id=value).exists():
            raise ValueError(f"Invalid report ID: {value}")
        return value

    @field_validator("report_modifier_id")
    @classmethod
    def validate_report_modifier_id(cls, value: Optional[int]) -> Optional[int]:
        if value:
            from api.models.report import ReportModifier

            if not ReportModifier.objects.filter(id=value).exists():
                raise ValueError(f"Invalid report modifier ID: {value}")
        return value


class JobStatusUpdateSchemaIn(Schema):
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]


class JobSchemaOut(Schema):
    id: int
    report_id: int
    report_modifier_id: Optional[int]
    status: str
    created: str
    updated: str


class PaginatedJobSchemaOut(Schema):
    items: List[JobSchemaOut]
    total: int
    page: int
    per_page: int
    total_pages: int
