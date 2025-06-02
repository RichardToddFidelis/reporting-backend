from ninja import Schema
from pydantic.types import Literal, datetime
from typing import List


class JobSchemaIn(Schema):
    report_id: int
    status: str = "PENDING"


class JobStatusUpdateSchemaIn(Schema):
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]


class JobSchemaOut(JobSchemaIn):
    created: datetime
    updated: datetime


class PaginatedJobSchemaOut(Schema):
    items: List[JobSchemaOut]
    total: int
    page: int
    per_page: int
    total_pages: int
