from ninja import NinjaAPI
from django.db.utils import OperationalError
from ninja.errors import ValidationError as NinjaValidationError
from .models.job import Job
from .schemas import JobSchemaIn, JobSchemaOut, ErrorSchema
import logging

logger = logging.getLogger(__name__)

api = NinjaAPI()

# Global exception handlers


@api.exception_handler(OperationalError)
def handle_db_error(request, exc):
    logger.error(f"Database error occurred: {str(exc)}", exc_info=True)
    return api.create_response(
        request,
        {"message": f"Database error: {str(exc)}"},
        status=500,
        schema=ErrorSchema,
    )


@api.exception_handler(NinjaValidationError)
def handle_validation_error(request, exc):
    logger.error(f"Validation error: {str(exc)}", exc_info=True)
    return api.create_response(
        request,
        {"message": str(exc)},
        status=400,
        schema=ErrorSchema,
    )


@api.exception_handler(Exception)
def handle_generic_error(request, exc):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return api.create_response(
        request,
        {"message": "An unexpected error occurred"},
        status=500,
        schema=ErrorSchema,
    )


# Job creation endpoint


@api.post("/jobs", response={201: JobSchemaOut, 400: ErrorSchema, 500: ErrorSchema})
async def create_job(request, payload: JobSchemaIn):
    try:
        job = await Job.objects.acreate(**payload.dict())
        return 201, JobSchemaOut.from_orm(job)
    except OperationalError as e:
        return 500, {"message": f"Database error: {str(e)}"}
    except Exception as e:
        return 500, {"message": f"Unexpected error: {str(e)}"}
