import logging
from django.urls import path
from ninja import NinjaAPI
from django.http import Http404
from django.core.exceptions import ValidationError
from api.controllers.jobs import job_router
from api.controllers.events import event_router
from api.controllers.reports import report_router
from schemas import ErrorSchema

# Configure logger
logger = logging.getLogger(__name__)

# Initialize NinjaAPI
api = NinjaAPI()

# Global exception handler for all routers


def custom_exception_handler(request, exc):
    logger.exception(f"Unhandled error in {request.method} {request.path}: {str(exc)}")
    if isinstance(exc, Http404):
        return api.create_response(
            request, {"message": str(exc) or "Resource not found"}, status=404
        )
    elif isinstance(exc, ValidationError):
        return api.create_response(
            request, {"message": f"Validation error: {str(exc)}"}, status=422
        )
    return api.create_response(
        request,
        {"message": "An unexpected error occurred. Please try again later."},
        status=500,
    )


# Register the global exception handler
api.add_exception_handler(Exception, custom_exception_handler)

# Register routers
api.add_router("/events/", event_router)
api.add_router("/reports/", report_router)
api.add_router("/jobs/", job_router)

# URL patterns
urlpatterns = [
    path("api/", api.urls),  # Include API URLs under /api/
]
