# reporting-backend/api/controllers/job.py
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage
from django.db import transaction
from api.models.job import Job
from api.models.report import Report, ReportModifier
from api.schemas.job import JobSchemaIn, JobSchemaOut, JobStatusUpdateSchemaIn, PaginatedJobSchemaOut
from api.schemas.error import ErrorSchema
from typing import List

logger = logging.getLogger(__name__)

job_router = Router(tags=["Jobs"])

@job_router.post(
    "/",
    response={201: JobSchemaOut, 404: ErrorSchema, 422: ErrorSchema},
    description="Create a new job for a report and optional modifier.",
)
def create_job(request, data: JobSchemaIn):
    """
    Creates a job for a specific report and optional modifier.

    **Details**:
    - **Request Body**:
      - `report_id`: Report ID.
      - `report_modifier_id`: Optional modifier ID.
      - `status`: Job status (default: PENDING).
    - **Success Response** (201): Created job details.
    - **Error Responses**:
      - **404**: Report or modifier not found.
      - **422**: Validation errors.
    """
    try:
        with transaction.atomic():
            report = get_object_or_404(Report, id=data.report_id)
            report_modifier = None
            if data.report_modifier_id:
                report_modifier = get_object_or_404(ReportModifier, id=data.report_modifier_id)
                if not report_modifier.reports.filter(id=data.report_id).exists():
                    return 422, {"message": "Report modifier is not linked to the specified report"}
            job = Job.objects.create(
                report=report,
                report_modifier=report_modifier,
                status=data.status,
            )
            return 201, JobSchemaOut(
                id=job.id,
                report_id=job.report.id,
                report_modifier_id=job.report_modifier.id if job.report_modifier else None,
                status=job.status,
                created=job.created.isoformat(),
                updated=job.updated.isoformat(),
            )
    except ValidationError as e:
        logger.error(
            f"Validation error in create_job: user={request.user if request.user.is_authenticated else 'anonymous'}, "
            f"input_report_id={data.report_id}, error={str(e)}"
        )
        return 422, {"message": str(e)}

@job_router.patch(
    "/{id}/",
    response={200: JobSchemaOut, 404: ErrorSchema, 422: ErrorSchema},
    description="Update the status of a job.",
)
def update_job_status(request, id: int, data: JobStatusUpdateSchemaIn):
    """
    Updates the status of a specific job.

    **Details**:
    - **Path Parameter**: `id` (job ID).
    - **Request Body**: `status` (PENDING, RUNNING, COMPLETED, FAILED).
    - **Success Response** (200): Updated job details.
    - **Error Responses**:
      - **404**: Job not found.
      - **422**: Validation errors.
    """
    try:
        with transaction.atomic():
            job = get_object_or_404(Job, id=id)
            job.status = data.status
            job.save()
            return 200, JobSchemaOut(
                id=job.id,
                report_id=job.report.id,
                report_modifier_id=job.report_modifier.id if job.report_modifier else None,
                status=job.status,
                created=job.created.isoformat(),
                updated=job.updated.isoformat(),
            )
    except ValidationError as e:
        logger.error(f"Validation error in update_job_status: job_id={id}, error={str(e)}")
        return 422, {"message": str(e)}

@job_router.get(
    "/{id}/",
    response={200: JobSchemaOut, 404: ErrorSchema},
    description="Retrieve a job by ID.",
)
def get_job(request, id: int):
    """
    Fetches details of a specific job by its ID.

    **Details**:
    - **Path Parameter**: `id` (job ID).
    - **Success Response** (200): Job details.
    - **Error Responses**:
      - **404**: Job not found.
    """
    job = get_object_or_404(Job, id=id)
    return 200, JobSchemaOut(
        id=job.id,
        report_id=job.report.id,
        report_modifier_id=job.report_modifier.id if job.report_modifier else None,
        status=job.status,
        created=job.created.isoformat(),
        updated=job.updated.isoformat(),
    )

@job_router.get(
    "/",
    response={200: PaginatedJobSchemaOut, 422: ErrorSchema},
    description="List all jobs with pagination.",
)
def list_jobs(request, page: int = 1, per_page: int = 10):
    """
    Retrieves a paginated list of all jobs.

    **Details**:
    - **Query Parameters**:
      - `page`: Page number (default: 1).
      - `per_page`: Items per page (default: 10).
    - **Success Response** (200): Paginated list of jobs.
    - **Error Responses**:
      - **422**: Invalid page number.
    """
    try:
        jobs = Job.objects.all().order_by("id")
        paginator = Paginator(jobs, per_page)
        page_obj = paginator.page(page)
        items = [
            JobSchemaOut(
                id=job.id,
                report_id=job.report.id,
                report_modifier_id=job.report_modifier.id if job.report_modifier else None,
                status=job.status,
                created=job.created.isoformat(),
                updated=job.updated.isoformat(),
            )
            for job in page_obj.object_list
        ]
        return 200, PaginatedJobSchemaOut(
            items=items,
            total=paginator.count,
            page=page,
            per_page=per_page,
            total_pages=paginator.num_pages,
        )
    except InvalidPage:
        logger.warning(f"Invalid page number {page} in list_jobs")
        return 422, {"message": f"Invalid page number: {page}"}
