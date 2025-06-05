# reporting-backend/api/controllers/report.py
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage
from django.db import transaction
from api.models.event import Event, EventGroup
from api.models.report import Report, ReportModifier
from api.schemas.event import EventSchemaOut, EventGroupSchemaOut
from api.schemas.report import (
    ReportSchemaIn,
    ReportCreateSchemaOut,
    ReportSchemaOut,
    ReportModifierSchemaIn,
    ReportModifierSchemaOut,
    ReportWithModifierSchemaOut,
    ReportWithModifiersSchemaOut,
    PaginatedReportSchemaOut,
    ReportWithEventGroupSchemaOut,
    ReportWithEventGroupsSchemaOut,
    EventGroupWithEventsSchemaOut,
    ReportWithModifierAndEventGroupSchemaOut,
)
from api.schemas.error import ErrorSchema
from typing import List

# Configure logger
logger = logging.getLogger(__name__)

report_router = Router(tags=["Report"])


# Utility functions to reduce redundancy
def to_report_schema_out(report: Report) -> ReportSchemaOut:
    """Convert a Report object to ReportSchemaOut."""
    return ReportSchemaOut(
        id=report.id,
        name=report.name,
        peril=report.peril,
        dr=report.dr,
        event_groups=list(report.event_groups.values_list("id", flat=True)),
        cron=report.cron,
        cob=report.cob,
        loss_perspective=report.loss_perspective,
        is_apply_calibration=report.is_apply_calibration,
        is_apply_inflation=report.is_apply_inflation,
        is_tag_outwards_ptns=report.is_tag_outwards_ptns,
        is_location_breakout=report.is_location_breakout,
        is_ignore_missing_lat_lon=report.is_ignore_missing_lat_lon,
        location_breakout_max_events=report.location_breakout_max_events,
        location_breakout_max_locations=report.location_breakout_max_locations,
        priority=report.priority,
        ncores=report.ncores,
        gross_node_id=report.gross_node_id,
        net_node_id=report.net_node_id,
        rollup_context_id=report.rollup_context_id,
        dynamic_ring_loss_threshold=report.dynamic_ring_loss_threshold,
        blast_radius=report.blast_radius,
        no_overlap_radius=report.no_overlap_radius,
        is_valid=report.is_valid,
        created=report.created.isoformat(),
        updated=report.updated.isoformat(),
    )


def to_report_modifier_schema_out(modifier: ReportModifier) -> ReportModifierSchemaOut:
    """Convert a ReportModifier object to ReportModifierSchemaOut."""
    return ReportModifierSchemaOut(
        id=modifier.id,
        as_at_date=modifier.as_at_date.isoformat() if modifier.as_at_date else None,
        fx_date=modifier.fx_date.isoformat() if modifier.fx_date else None,
        report_ids=list(modifier.reports.values_list("id", flat=True)),
        quarter=modifier.quarter,
        year=modifier.year,
        month=modifier.month,
        day=modifier.day,
    )


@report_router.post(
    "/reports/",
    response={201: ReportCreateSchemaOut, 422: ErrorSchema},
    tags=["Report"],
    description="Create a new report.",
)
def create_report(request, data: ReportSchemaIn):
    """
    Creates a report with specified details and associated event groups.

    **Details**:
    - **Request Body**: Report details (name, peril, etc.).
    - **Success Response** (201): Created report ID and name.
    - **Error Responses**:
      - **422**: Invalid event group IDs or validation errors.
    """
    try:
        with transaction.atomic():
            data_dict = data.dict(exclude={"event_groups"})
            report = Report.objects.create(**data_dict)
            if data.event_groups:
                event_groups = EventGroup.objects.filter(id__in=data.event_groups)
                report.event_groups.set(event_groups)
            return 201, ReportCreateSchemaOut(
                id=report.id,
                name=report.name,
            )
    except ValidationError as e:
        logger.error(
            f"Validation error in create_report: user={request.user if request.user.is_authenticated else 'anonymous'}, "
            f"input_name={data.name}, error={str(e)}"
        )
        return 422, {"message": str(e)}


@report_router.get(
    "/reports/{id}/",
    response={200: ReportSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report by ID.",
)
def get_report(request, id: int):
    """
    Fetches details of a specific report by its ID.

    **Details**:
    - **Path Parameter**: `id` (report ID).
    - **Success Response** (200): Report details.
    - **Error Responses**:
      - **404**: Report not found.
    """
    report = get_object_or_404(Report, id=id)
    return 200, to_report_schema_out(report)


@report_router.get(
    "/reports/",
    response={200: PaginatedReportSchemaOut, 422: ErrorSchema},
    tags=["Report"],
    description="List all reports with pagination.",
)
def list_reports(request, page: int = 1, per_page: int = 10):
    """
    Retrieves a paginated list of all reports.

    **Details**:
    - **Query Parameters**:
      - `page`: Page number (default: 1).
      - `per_page`: Items per page (default: 10).
    - **Success Response** (200): Paginated list of reports.
    - **Error Responses**:
      - **422**: Invalid page number.
    """
    try:
        reports = Report.objects.all().order_by("id")
        paginator = Paginator(reports, per_page)
        page_obj = paginator.page(page)
        items = [to_report_schema_out(report) for report in page_obj.object_list]
        return 200, PaginatedReportSchemaOut(
            items=items,
            total=paginator.count,
            page=page,
            per_page=per_page,
            total_pages=paginator.num_pages,
        )
    except InvalidPage:
        logger.warning(f"Invalid page number {page} in list_reports")
        return 422, {"message": f"Invalid page number: {page}"}


@report_router.post(
    "/report-modifiers/",
    response={201: ReportModifierSchemaOut, 422: ErrorSchema},
    tags=["Report"],
    description="Create a new report modifier and optionally link it to reports.",
)
def create_report_modifier(request, data: ReportModifierSchemaIn):
    """
    Creates a modifier and optionally links it to specified reports.

    **Details**:
    - **Request Body**:
      - `as_at_date`: Optional date (ISO format).
      - `fx_date`: Optional date (ISO format).
      - `report_ids`: Optional list of report IDs to link.
    - **Success Response** (201): Created modifier details.
    - **Error Responses**:
      - **422**: Validation errors.
    """
    try:
        with transaction.atomic():
            modifier = ReportModifier.objects.create(
                as_at_date=data.as_at_date,
                fx_date=data.fx_date,
            )
            if data.report_ids:
                reports = Report.objects.filter(id__in=data.report_ids)
                modifier.reports.set(reports)
            return 201, to_report_modifier_schema_out(modifier)
    except ValidationError as e:
        logger.error(
            f"Validation error in create_report_modifier: user={request.user if request.user.is_authenticated else 'anonymous'}, "
            f"input_as_at_date={data.as_at_date}, error={str(e)}"
        )
        return 422, {"message": str(e)}


@report_router.get(
    "/report-modifiers/{id}/",
    response={200: ReportModifierSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report modifier by ID.",
)
def get_report_modifier(request, id: int):
    """
    Fetches details of a specific report modifier by its ID.

    **Details**:
    - **Path Parameter**: `id` (modifier ID).
    - **Success Response** (200): Modifier details.
    - **Error Responses**:
      - **404**: Modifier not found.
    """
    modifier = get_object_or_404(ReportModifier, id=id)
    return 200, to_report_modifier_schema_out(modifier)


@report_router.post(
    "/report-modifiers/{modifier_id}/link-reports/",
    response={200: ReportModifierSchemaOut, 404: ErrorSchema, 422: ErrorSchema},
    tags=["Report"],
    description="Link a report modifier to multiple reports.",
)
def link_modifier_to_reports(request, modifier_id: int, report_ids: List[int]):
    """
    Links an existing report modifier to multiple reports.

    **Details**:
    - **Path Parameter**: `modifier_id` (modifier ID).
    - **Request Body**: List of report IDs.
    - **Success Response** (200): Updated modifier details.
    - **Error Responses**:
      - **404**: Modifier or reports not found.
      - **422**: Validation errors.
    """
    try:
        with transaction.atomic():
            modifier = get_object_or_404(ReportModifier, id=modifier_id)
            reports = Report.objects.filter(id__in=report_ids)
            if len(reports) != len(report_ids):
                invalid_ids = set(report_ids) - set(
                    reports.values_list("id", flat=True)
                )
                return 422, {"message": f"Invalid report IDs: {invalid_ids}"}
            modifier.reports.add(*reports)
            return 200, to_report_modifier_schema_out(modifier)
    except ValidationError as e:
        logger.error(
            f"Validation error in link_modifier_to_reports: modifier_id={modifier_id}, "
            f"report_ids={report_ids}, error={str(e)}"
        )
        return 422, {"message": str(e)}


@report_router.get(
    "/reports/{id}/modifiers/",
    response={200: ReportWithModifiersSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report with its modifiers.",
)
def get_report_with_modifiers(request, id: int):
    """
    Fetches a report and its associated modifiers by report ID.

    **Details**:
    - **Path Parameter**: `id` (report ID).
    - **Success Response** (200): Report and modifier details.
    - **Error Responses**:
      - **404**: Report not found.
    """
    report = get_object_or_404(Report, id=id)
    modifiers = report.modifiers.all()
    return 200, ReportWithModifiersSchemaOut(
        report=to_report_schema_out(report),
        modifiers=[to_report_modifier_schema_out(modifier) for modifier in modifiers],
    )


@report_router.get(
    "/reports/{id}/event-groups/",
    response={200: ReportWithEventGroupsSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report with its event groups and associated events.",
)
def get_report_with_event_groups(request, id: int):
    """
    Fetches a report with its associated event groups and their event details by report ID.

    **Details**:
    - **Path Parameter**: `id` (report ID).
    - **Success Response** (200): Report, event groups, and events.
    - **Error Responses**:
      - **404**: Report not found.
    """
    report = get_object_or_404(Report, id=id)
    event_groups = report.event_groups.all()
    return 200, ReportWithEventGroupsSchemaOut(
        report=to_report_schema_out(report),
        event_groups=[
            EventGroupWithEventsSchemaOut(
                event_group=EventGroupSchemaOut(
                    id=eg.id,
                    name=eg.name,
                    event_ids=list(eg.events.values_list("id", flat=True)),
                    created=eg.created.isoformat(),
                    updated=eg.updated.isoformat(),
                ),
                events=[EventSchemaOut.from_orm(event) for event in eg.events.all()],
            )
            for eg in event_groups
        ],
    )


@report_router.post(
    "/reports/{report_id}/link-event-group/{event_group_id}/",
    response={200: ReportWithEventGroupSchemaOut, 404: ErrorSchema, 422: ErrorSchema},
    tags=["Report"],
    description="Link an existing event group to an existing report.",
)
def link_report_to_event_group(request, report_id: int, event_group_id: int):
    """
    Adds an existing event group to an existing report's event_groups.

    **Details**:
    - **Path Parameters**:
      - `report_id`: ID of the report.
      - `event_group_id`: ID of the event group to link.
    - **Success Response** (200): Linked report and event group IDs.
    - **Error Responses**:
      - **404**: Report or event group not found.
      - **422**: Event group already linked or validation errors.
    """
    try:
        with transaction.atomic():
            report = get_object_or_404(Report, id=report_id)
            event_group = get_object_or_404(EventGroup, id=event_group_id)
            if report.event_groups.filter(id=event_group_id).exists():
                return 422, {"message": "Event group is already linked to this report"}
            report.event_groups.add(event_group)
            return 200, ReportWithEventGroupSchemaOut(
                report_id=report.id,
                event_group_id=event_group.id,
            )
    except ValidationError as e:
        logger.error(
            f"Validation error in link_report_to_event_group: report_id={report_id}, "
            f"event_group_id={event_group_id}, error={str(e)}"
        )
        return 422, {"message": str(e)}


@report_router.get(
    "/reports/{report_id}/modifiers/{modifier_id}/",
    response={200: ReportWithModifiersSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report and a specific modifier by their IDs.",
)
def get_report_and_modifier(request, report_id: int, modifier_id: int):
    """
    Fetches a report and a specific modifier by report ID and modifier ID.

    **Details**:
    - **Path Parameters**:
      - `report_id`: ID of the report.
      - `modifier_id`: ID of the modifier.
    - **Success Response** (200): Report and modifier details.
    - **Error Responses**:
      - **404**: Report or modifier not found or not linked.
    """
    report = get_object_or_404(Report, id=report_id)
    modifier = get_object_or_404(ReportModifier, id=modifier_id)
    if not modifier.reports.filter(id=report_id).exists():
        return 404, {"message": "Modifier is not linked to this report"}
    return 200, ReportWithModifiersSchemaOut(
        report=to_report_schema_out(report),
        modifiers=[to_report_modifier_schema_out(modifier)],
    )


@report_router.get(
    "/reports/{report_id}/event-groups/{event_group_id}/",
    response={200: ReportWithEventGroupsSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report and a specific event group by their IDs.",
)
def get_report_and_event_group(request, report_id: int, event_group_id: int):
    """
    Fetches a report and a specific event group by report ID and event group ID.

    **Details**:
    - **Path Parameters**:
      - `report_id`: ID of the report.
      - `event_group_id`: ID of the event group.
    - **Success Response** (200): Report and event group details.
    - **Error Responses**:
      - **404**: Report or event group not found or not linked.
    """
    report = get_object_or_404(Report, id=report_id)
    event_group = get_object_or_404(EventGroup, id=event_group_id)
    if not report.event_groups.filter(id=event_group_id).exists():
        return 404, {"message": "Event group is not linked to this report"}
    return 200, ReportWithEventGroupsSchemaOut(
        report=to_report_schema_out(report),
        event_groups=[
            EventGroupWithEventsSchemaOut(
                event_group=EventGroupSchemaOut(
                    id=event_group.id,
                    name=event_group.name,
                    event_ids=list(event_group.events.values_list("id", flat=True)),
                    created=event_group.created.isoformat(),
                    updated=event_group.updated.isoformat(),
                ),
                events=[EventSchemaOut.from_orm(event) for event in eg.events.all()],
            )
        ],
    )


@report_router.get(
    "/reports/{report_id}/modifiers/{modifier_id}/event-groups/{event_group_id}/",
    response={200: ReportWithModifierAndEventGroupSchemaOut, 404: ErrorSchema},
    tags=["Report"],
    description="Retrieve a report, a specific modifier, and a specific event group by their IDs.",
)
def get_report_with_modifier_and_event_group(
    request, report_id: int, modifier_id: int, event_group_id: int
):
    """
    Fetches a report, a specific modifier, and a specific event group by their IDs.

    **Details**:
    - **Path Parameters**:
      - `report_id`: ID of the report.
      - `modifier_id`: ID of the modifier.
      - `event_group_id`: ID of the event group.
    - **Success Response** (200): Report, modifier, and event group details.
    - **Error Responses**:
      - **404**: Report, modifier, or event group not found or not linked.
    """
    report = get_object_or_404(Report, id=report_id)
    modifier = get_object_or_404(ReportModifier, id=modifier_id)
    event_group = get_object_or_404(EventGroup, id=event_group_id)
    if not modifier.reports.filter(id=report_id).exists():
        return 404, {"message": "Modifier is not linked to this report"}
    if not report.event_groups.filter(id=event_group_id).exists():
        return 404, {"message": "Event group is not linked to this report"}
    return 200, ReportWithModifierAndEventGroupSchemaOut(
        report=to_report_schema_out(report),
        modifier=to_report_modifier_schema_out(modifier),
        event_group=EventGroupWithEventsSchemaOut(
            event_group=EventGroupSchemaOut(
                id=event_group.id,
                name=event_group.name,
                event_ids=list(event_group.events.values_list("id", flat=True)),
                created=event_group.created.isoformat(),
                updated=event_group.updated.isoformat(),
            ),
            events=[
                EventSchemaOut.from_orm(event) for event in event_group.events.all()
            ],
        ),
    )

