# reporting-backend/api/schemas/report.py
from ninja import Schema
from typing import List, Optional
from api.schemas.event import EventSchemaOut, EventGroupSchemaOut
from api.models.event import EventGroup
from pydantic import field_validator


class ReportSchemaIn(Schema):
    name: str
    peril: str
    dr: float = 1.0
    event_groups: Optional[List[int]] = None
    cron: Optional[str] = None
    cob: Optional[str] = None
    loss_perspective: str
    is_apply_calibration: bool = True
    is_apply_inflation: bool = True
    is_tag_outwards_ptns: bool = False
    is_location_breakout: bool = False
    is_ignore_missing_lat_lon: bool = True
    location_breakout_max_events: int = 500000
    location_breakout_max_locations: int = 1000000
    priority: str = "AboveNormal"
    ncores: int = 24
    gross_node_id: Optional[int] = None
    net_node_id: Optional[int] = None
    rollup_context_id: Optional[int] = None
    dynamic_ring_loss_threshold: int = 5000000
    blast_radius: Optional[float] = 50
    no_overlap_radius: Optional[float] = None
    is_valid: bool = True

    @field_validator("event_groups")
    @classmethod
    def validate_event_groups(cls, value: Optional[List[int]]) -> Optional[List[int]]:
        if value:
            existing_groups = EventGroup.objects.filter(id__in=value).values_list(
                "id", flat=True
            )
            if len(existing_groups) != len(value):
                invalid_ids = set(value) - set(existing_groups)
                raise ValueError(f"Invalid event group IDs: {invalid_ids}")
        return value


class ReportCreateSchemaOut(Schema):
    id: int
    name: str


class ReportSchemaOut(Schema):
    id: int
    name: str
    peril: str
    dr: float
    event_groups: List[int]
    cron: Optional[str]
    cob: Optional[str]
    loss_perspective: str
    is_apply_calibration: bool
    is_apply_inflation: bool
    is_tag_outwards_ptns: bool
    is_location_breakout: bool
    is_ignore_missing_lat_lon: bool
    location_breakout_max_events: int
    location_breakout_max_locations: int
    priority: str
    ncores: int
    gross_node_id: Optional[int]
    net_node_id: Optional[int]
    rollup_context_id: Optional[int]
    dynamic_ring_loss_threshold: int
    blast_radius: Optional[float]
    no_overlap_radius: Optional[float]
    is_valid: bool
    created: str
    updated: str


class ReportModifierSchemaIn(Schema):
    report_id: int
    as_at_date: Optional[str] = None
    fx_date: Optional[str] = None


class ReportModifierSchemaOut(Schema):
    id: int
    report_id: int
    as_at_date: Optional[str]
    fx_date: Optional[str]
    quarter: Optional[int]
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]


class ReportWithModifierSchemaOut(Schema):
    report_id: int
    report_modifier_id: int


class ReportWithModifiersSchemaOut(Schema):
    report: ReportSchemaOut
    modifiers: List[ReportModifierSchemaOut]


class PaginatedReportSchemaOut(Schema):
    items: List[ReportSchemaOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class ReportWithEventGroupSchemaOut(Schema):
    report_id: int
    event_group_id: int


class EventGroupWithEventsSchemaOut(Schema):
    event_group: EventGroupSchemaOut
    events: List[EventSchemaOut]


class ReportWithEventGroupsSchemaOut(Schema):
    report: ReportSchemaOut
    event_groups: List[EventGroupWithEventsSchemaOut]


class ReportWithModifierAndEventGroupSchemaOut(Schema):
    report: ReportSchemaOut
    modifier: ReportModifierSchemaOut
    event_group: EventGroupWithEventsSchemaOut
