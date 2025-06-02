import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage
from api.models import Report, ReportModifier, EventGroup
from api.schemas import (
    ReportSchemaIn,
    ReportSchemaOut,
    ReportModifierSchemaIn,
    ReportModifierSchemaOut,
    PaginatedReportSchemaOut,
    ErrorSchema,
)

# Configure logger
logger = logging.getLogger(__name__)

report_router = Router(tags=["Report"])


@report_router.post("/reports/", response={201: ReportSchemaOut, 422: ErrorSchema})
def create_report(request, data: ReportSchemaIn):
    try:
        data_dict = data.dict(exclude={"event_groups"})
        report = Report.objects.create(**data_dict)
        if data.event_groups:
            event_groups = EventGroup.objects.filter(id__in=data.event_groups)
            if len(event_groups) != len(data.event_groups):
                report.delete()
                return 422, {"message": "One or more event group IDs are invalid"}
            report.event_groups.set(event_groups)
        return 201, {
            **ReportSchemaOut.from_orm(report).dict(),
            "event_groups": list(report.event_groups.values_list("id", flat=True)),
            "created": report.created.isoformat(),
            "updated": report.updated.isoformat(),
        }
    except ValidationError as e:
        logger.error(f"Validation error in create_report: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@report_router.get("/reports/{id}/", response={200: ReportSchemaOut, 404: ErrorSchema})
def get_report(request, id: int):
    report = get_object_or_404(Report, id=id)
    return 200, {
        **ReportSchemaOut.from_orm(report).dict(),
        "event_groups": list(report.event_groups.values_list("id", flat=True)),
        "created": report.created.isoformat(),
        "updated": report.updated.isoformat(),
    }


@report_router.get(
    "/reports/", response={200: PaginatedReportSchemaOut, 422: ErrorSchema}
)
def list_reports(request, page: int = 1, per_page: int = 10):
    try:
        reports = Report.objects.all().order_by("id")
        paginator = Paginator(reports, per_page)
        page_obj = paginator.page(page)
        items = [
            {
                **ReportSchemaOut.from_orm(report).dict(),
                "event_groups": list(report.event_groups.values_list("id", flat=True)),
                "created": report.created.isoformat(),
                "updated": report.updated.isoformat(),
            }
            for report in page_obj.object_list
        ]
        return 200, {
            "items": items,
            "total": paginator.count,
            "page": page,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
        }
    except InvalidPage:
        logger.warning(f"Invalid page number {page} in list_reports")
        return 422, {"message": f"Invalid page number: {page}"}


@report_router.post(
    "/report-modifiers/",
    response={201: ReportModifierSchemaOut, 404: ErrorSchema, 422: ErrorSchema},
)
def create_report_modifier(request, data: ReportModifierSchemaIn):
    try:
        report = get_object_or_404(Report, id=data.report_id)
        modifier = ReportModifier.objects.create(
            report=report, **data.dict(exclude={"report_id"})
        )
        return 201, modifier
    except ValidationError as e:
        logger.error(f"Validation error in create_report_modifier: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@report_router.get(
    "/report-modifiers/{id}/", response={200: ReportModifierSchemaOut, 404: ErrorSchema}
)
def get_report_modifier(request, id: int):
    modifier = get_object_or_404(ReportModifier, id=id)
    return 200, modifier
