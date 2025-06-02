import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from api.models import Event, EventGroup, RingEvent, BoxEvent, GeoEvent
from api.schemas import (
    RingEventSchemaIn,
    RingEventSchemaOut,
    BoxEventSchemaIn,
    BoxEventSchemaOut,
    GeoEventSchemaIn,
    GeoEventSchemaOut,
    EventGroupCreateSchemaIn,
    EventGroupSchemaOut,
    ErrorSchema,
)
from typing import List

# Configure logger
logger = logging.getLogger(__name__)

event_router = Router(tags=["Events"])


@event_router.post(
    "/ring-events/",
    response={201: RingEventSchemaOut, 422: ErrorSchema},
    tags=["Events/Ring"],
)
def create_ring_event(request, data: RingEventSchemaIn):
    try:
        ring_event = RingEvent.objects.create(**data.dict())
        return 201, ring_event
    except ValidationError as e:
        logger.error(f"Validation error in create_ring_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/ring-events/{id}/",
    response={200: RingEventSchemaOut, 404: ErrorSchema},
    tags=["Events/Ring"],
)
def get_ring_event(request, id: int):
    ring_event = get_object_or_404(RingEvent, id=id)
    return 200, ring_event


@event_router.get(
    "/ring-events/", response=List[RingEventSchemaOut], tags=["Events/Ring"]
)
def list_ring_events(request):
    return RingEvent.objects.all()


@event_router.post(
    "/box-events/",
    response={201: BoxEventSchemaOut, 422: ErrorSchema},
    tags=["Events/Box"],
)
def create_box_event(request, data: BoxEventSchemaIn):
    try:
        box_event = BoxEvent.objects.create(**data.dict())
        return 201, box_event
    except ValidationError as e:
        logger.error(f"Validation error in create_box_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/box-events/{id}/",
    response={200: BoxEventSchemaOut, 404: ErrorSchema},
    tags=["Events/Box"],
)
def get_box_event(request, id: int):
    box_event = get_object_or_404(BoxEvent, id=id)
    return 200, box_event


@event_router.get("/box-events/", response=List[BoxEventSchemaOut], tags=["Events/Box"])
def list_box_events(request):
    return BoxEvent.objects.all()


@event_router.post(
    "/geo-events/",
    response={201: GeoEventSchemaOut, 422: ErrorSchema},
    tags=["Events/Geo"],
)
def create_geo_event(request, data: GeoEventSchemaIn):
    try:
        geo_event = GeoEvent.objects.create(**data.dict())
        return 201, geo_event
    except ValidationError as e:
        logger.error(f"Validation error in create_geo_event: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/geo-events/{id}/",
    response={200: GeoEventSchemaOut, 404: ErrorSchema},
    tags=["Events/Geo"],
)
def get_geo_event(request, id: int):
    geo_event = get_object_or_404(GeoEvent, id=id)
    return 200, geo_event


@event_router.get("/geo-events/", response=List[GeoEventSchemaOut], tags=["Events/Geo"])
def list_geo_events(request):
    return GeoEvent.objects.all()


# reporting-backend/api/controllers/events.py (partial)
@event_router.post(
    "/events/create-group/",
    response={201: EventGroupSchemaOut, 422: ErrorSchema},
    tags=["Events/Group"],
    description="Creates a new event group and assigns specified events to it.",
)
def create_event_group(request, data: EventGroupCreateSchemaIn):
    """
    Creates a new event group and associates it with a list of events in the reporting-backend system.
    ...
    """
    try:
        events = Event.objects.filter(id__in=data.event_ids)
        if len(events) != len(data.event_ids):
            return 422, {"message": "One or more event IDs are invalid"}
        group = EventGroup.objects.create(name=data.name)
        group.events.set(events)
        return 201, {
            "id": group.id,
            "name": group.name,
            "event_ids": list(group.events.values_list("id", flat=True)),
            "created": group.created.isoformat(),
            "updated": group.updated.isoformat(),
        }
    except ValidationError as e:
        logger.error(f"Validation error in create_event_group: {str(e)}")
        return 422, {"message": f"Validation error: {str(e)}"}


@event_router.get(
    "/event-group/{id}/",
    response={200: EventGroupSchemaOut, 404: ErrorSchema},
    tags=["Events/Group"],
    description="Retrieve an event group by ID.",
)
def get_event_group(request, id: int):
    """
    Fetches details of a specific event group by its ID.

    **Details**:
    - **Path Parameter**:
      - `id`: The unique ID of the event group.
    - **Success Response** (200):
      - Returns the event group details, including ID, name, associated event IDs, and timestamps.
    - **Error Responses**:
      - **404**: If the event group with the given ID does not exist.

    **Example Response**:
    ```json
    {
      "id": 1,
      "name": "Test Group",
      "event_ids": [1, 2, 3],
      "created": "2025-06-02T14:00:00Z",
      "updated": "2025-06-02T14:00:00Z"
    }
    ```
    """
    group = get_object_or_404(EventGroup, id=id)
    return 200, {
        "id": group.id,
        "name": group.name,
        "event_ids": list(group.events.values_list("id", flat=True)),
        "created": group.created.isoformat(),
        "updated": group.created.isoformat(),
    }


@event_router.get(
    "/event-groups/",
    response=List[EventGroupSchemaOut],
    tags=["Events/Group"],
    description="List all event groups.",
)
def list_event_groups(request):
    """
    Retrieves a list of all event groups in the system.

    **Details**:
    - **Success Response** (200):
      - Returns a list of event groups, each including ID, name, associated event IDs, and timestamps.
    - **Error Responses**:
      - None (returns an empty list if no groups exist).

    **Example Response**:
    ```json
    [
      {
        "id": 1,
        "name": "Test Group",
        "event_ids": [1, 2, 3],
        "created": "2025-06-02T14:00:00Z",
        "updated": "2025-06-02T14:00:00Z"
      },
      {
        "id": 2,
        "name": "Another Group",
        "event_ids": [4, 5],
        "created": "2025-06-02T14:01:00Z",
        "updated": "2025-06-02T14:01:00Z"
      }
    ]
    ```
    """
    groups = EventGroup.objects.all()
    return [
        {
            "id": group.id,
            "name": group.name,
            "event_ids": list(group.events.values_list("id", flat=True)),
            "created": group.created.isoformat(),
            "updated": group.created.isoformat(),
        }
        for group in groups
    ]
