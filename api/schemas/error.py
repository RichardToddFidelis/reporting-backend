from ninja import Schema
from pydantic import field_validator, Field
from typing import Optional


class ErrorSchema(Schema):
    message: str
