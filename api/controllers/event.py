import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from myapp.models import Event, EventGroup, RingEvent, BoxEvent, GeoEvent
from myapp.schemas import (
    RingEventSchemaIn,
    RingEventSchemaOut,
    BoxEventSchemaIn,
    BoxEventSchemaOut,
    GeoEventSchemaIn,
    GeoEventSchemaOut,
    ErrorSchema,
)
from typing import List

# Configure logger
logger = logging.getLogger(__name__)

event_router = Router()


@event_router.post(
    "/ring-events/", response={201: RingEventSchemaOut, 422: ErrorSchema}
)
def create_ring_event(request, data: RingEventSchemaIn):
    try:
        ring_event = RingEvent.objects.create(**data.dict())
        return 201, ring_event
    except ValidationError as e:
        logger.error(f"Validation error in create_ring_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/ring-events/{id}/", response={200: RingEventSchemaOut, 404: ErrorSchema}
)
def get_ring_event(request, id: int):
    ring_event = get_object_or_404(RingEvent, id=id)
    return 200, ring_event


@event_router.get("/ring-events/", response=List[RingEventSchemaOut])
def list_ring_events(request):
    return RingEvent.objects.all()


@event_router.post("/box-events/", response={201: BoxEventSchemaOut, 422: ErrorSchema})
def create_box_event(request, data: BoxEventSchemaIn):
    try:
        box_event = BoxEvent.objects.create(**data.dict())
        return 201, box_event
    except ValidationError as e:
        logger.error(f"Validation error in create_box_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/box-events/{id}/", response={200: BoxEventSchemaOut, 404: ErrorSchema}
)
def get_box_event(request, id: int):
    box_event = get_object_or_404(BoxEvent, id=id)
    return 200, box_event


@event_router.get("/box-events/", response=List[BoxEventSchemaOut])
def list_box_events(request):
    return BoxEvent.objects.all()


@event_router.post("/geo-events/", response={201: GeoEventSchemaOut, 422: ErrorSchema})
def create_geo_event(request, data: GeoEventSchemaIn):
    try:
        geo_event = GeoEvent.objects.create(**data.dict())
        return 201, geo_event
    except ValidationError as e:
        logger.error(f"Validation error in create_geo_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/geo-events/{id}/", response={200: GeoEventSchemaOut, 404: ErrorSchema}
)
def get_geo_event(request, id: int):
    geo_event = get_object_or_404(GeoEvent, id=id)
    return 200, geo_event


@event_router.get("/geo-events/", response=List[GeoEventSchemaOut])
def list_geo_events(request):
    return GeoEvent.objects.all()


@event_router.post(
    "/events/{event_id}/assign-groups/",
    response={200: None, 404: ErrorSchema, 422: ErrorSchema},
)
def assign_event_to_groups(request, event_id: int, group_ids: List[int]):
    try:
        event = get_object_or_404(Event, id=event_id)
        groups = EventGroup.objects.filter(id__in=group_ids)
        if len(groups) != len(group_ids):
            return 422, {"message": "One or more group IDs are invalid"}
        event.event_groups.set(groups)
        return 200, None
    except ValidationError as e:
        logger.error(f"Validation error in assign_event_to_groups: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}

