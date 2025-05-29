from ninja import Schema
from pydantic.types import Literal


class JobSchemaIn(Schema):
    report_id: int
    status: str = "PENDING"


class JobStatusUpdateSchemaIn(Schema):
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]
