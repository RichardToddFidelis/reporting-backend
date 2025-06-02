# reporting-backend/api/controllers/job.py
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage
from api.models.job import Job
from api.models.report import Report
from api.schemas.job import (
    JobSchemaIn,
    JobStatusUpdateSchemaIn,
    JobSchemaOut,
    PaginatedJobSchemaOut,
)
from api.schemas.error import ErrorSchema

logger = logging.getLogger(__name__)

job_router = Router(tags=["Jobs"])


@job_router.post("/", response={201: JobSchemaOut, 404: ErrorSchema, 422: ErrorSchema})
def create_job(request, data: JobSchemaIn):
    try:
        report = get_object_or_404(Report, id=data.report_id)
        job = Job.objects.create(report=report, status=data.status)
        return 201, {
            **JobSchemaOut.from_orm(job).dict(),
            "created": job.created.isoformat(),
            "updated": job.updated.isoformat(),
        }
    except ValidationError as e:
        logger.error(f"Validation error in create_job: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@job_router.patch(
    "/{id}/", response={200: JobSchemaOut, 404: ErrorSchema, 422: ErrorSchema}
)
def update_job_status(request, id: int, data: JobStatusUpdateSchemaIn):
    try:
        job = get_object_or_404(Job, id=id)
        job.status = data.status
        job.save()
        return 200, {
            **JobSchemaOut.from_orm(job).dict(),
            "created": job.created.isoformat(),
            "updated": job.updated.isoformat(),
        }
    except ValidationError as e:
        logger.error(f"Validation error in update_job_status: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@job_router.get("/{id}/", response={200: JobSchemaOut, 404: ErrorSchema})
def get_job(request, id: int):
    job = get_object_or_404(Job, id=id)
    return 200, {
        **JobSchemaOut.from_orm(job).dict(),
        "created": job.created.isoformat(),
        "updated": job.updated.isoformat(),
    }


@job_router.get("/", response={200: PaginatedJobSchemaOut, 422: ErrorSchema})
def list_jobs(request, page: int = 1, per_page: int = 10):
    try:
        jobs = Job.objects.all().order_by("id")
        paginator = Paginator(jobs, per_page)
        page_obj = paginator.page(page)
        items = [
            {
                **JobSchemaOut.from_orm(job).dict(),
                "created": job.created.isoformat(),
                "updated": job.updated.isoformat(),
            }
            for job in page_obj.object_list
        ]
        return 200, {
            "items": items,
            "total": paginator.count,
            "page": page,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
        }
    except InvalidPage:
        logger.warning(f"Invalid page number {page} in list_jobs")
        return 422, {"message": f"Invalid page number: {page}"}
