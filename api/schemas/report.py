from ninja import Schema
from typing import List, Optional


# Schemas
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
    as_at_date: Optional[str]
    fx_date: Optional[str]
    report_id: int


class ReportModifierSchemaOut(Schema):
    id: int
    as_at_date: Optional[str]
    fx_date: Optional[str]
    report_id: int
    quarter: Optional[int]
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]


class ErrorSchema(Schema):
    message: str


class PaginatedReportSchemaOut(Schema):
    items: List[ReportSchemaOut]
    total: int
    page: int
    per_page: int
    total_pages: int
