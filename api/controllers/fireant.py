# reporting-backend/api/controllers/report.py
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage
from django.db import transaction
from typing import List

logger = logging.getLogger(__name__)

event_router = Router(tags=["fireant"])

class FireantSchemaIn(Schema):
    report_id: int
    report_modifier_id: int


@event_router.post(
    "/fireant/",
    response={201: RingEventSchemaOut, 422: ErrorSchema},
    tags=["fireant"],
    description="Create a fireant report",
)
def create_ring_event(request, data: FireantSchemaIn):
    """
    Creates a ring event with specified coordinates and radius.
    Returns the created event details on success.
    """



  
