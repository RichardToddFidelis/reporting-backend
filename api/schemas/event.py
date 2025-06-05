# reporting-backend/api/schemas/event.py
from ninja import Schema
from pydantic import field_validator, Field, ValidationInfo
from typing import Optional, List


# Base schema for common Event fields (used in input schemas)
class EventSchemaIn(Schema):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=255)
    is_valid: bool = True


# Base schema for common Event fields (used in output schemas)
class EventSchemaOut(Schema):
    id: int
    name: str
    description: str
    is_valid: bool


# RingEvent Schemas
class RingEventSchemaIn(EventSchemaIn):
    latitude: float
    longitude: float
    radius: float = Field(..., ge=0)

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value


class RingEventSchemaOut(EventSchemaOut):
    latitude: float
    longitude: float


# BoxEvent Schemas
class BoxEventSchemaIn(EventSchemaIn):
    max_lat: float
    min_lat: float
    max_lon: float
    min_lon: float

    @field_validator("max_lat", "min_lat")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @field_validator("max_lon", "min_lon")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value

    @field_validator("max_lat")
    @classmethod
    def validate_max_lat(cls, value: float, info: ValidationInfo) -> float:
        if info.data.get("min_lat") is not None and value <= info.data["min_lat"]:
            raise ValueError("max_lat must be greater than min_lat.")
        return value

    @field_validator("max_lon")
    @classmethod
    def validate_max_lon(cls, value: float, info: ValidationInfo) -> float:
        if info.data.get("min_lon") is not None and value <= info.data["min_lon"]:
            raise ValueError("max_lon must be greater than min_lon.")
        return value


class BoxEventSchemaOut(EventSchemaOut):
    max_lat: float
    min_lat: float
    max_lon: float
    min_lon: float


# GeoEvent Schemas
class GeoEventSchemaIn(EventSchemaIn):
    country: Optional[str] = Field(None, max_length=255)
    area: Optional[str] = Field(None, max_length=255)
    subarea: Optional[str] = Field(None, max_length=255)
    subarea2: Optional[str] = Field(None, max_length=255)


class GeoEventSchemaOut(EventSchemaOut):
    country: Optional[str]
    area: Optional[str]
    subarea: Optional[str]
    subarea2: Optional[str]


class EventGroupCreateSchemaIn(Schema):
    name: str = ""  # Optional group name
    event_ids: List[int]  # List of event IDs


class EventGroupSchemaOut(Schema):
    id: int
    name: str
    event_ids: List[int]
    created: str
    updated: str


class EventGroupWithEventsSchemaOut(Schema):
    event_group: EventGroupSchemaOut
    events: List[EventSchemaOut]


class ErrorSchema(Schema):
    message: str
