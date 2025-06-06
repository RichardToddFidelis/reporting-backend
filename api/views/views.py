from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from api.models.report import Report, ReportModifier
from api.models.job import Job
from api.models.event import Event, EventGroup, RingEvent, BoxEvent, GeoEvent
from .serializers import (
    ReportSerializer,
    ReportModifierSerializer,
    JobSerializer,
    EventSerializer,
    EventGroupSerializer,
    RingEventSerializer,
    BoxEventSerializer,
    GeoEventSerializer,
    ReportWithModifierSerializer,
)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    @action(detail=True, methods=["get"], url_path="modifiers")
    def get_report_with_modifiers(self, request, pk=None):
        report = self.get_object()
        serializer = ReportSerializer(report, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="modifier/<int:modifier_id>")
    def get_report_with_specific_modifier(self, request, pk=None, modifier_id=None):
        report = self.get_object()
        try:
            modifier = ReportModifier.objects.get(id=modifier_id, reports=report)
        except ReportModifier.DoesNotExist:
            raise NotFound(
                "ReportModifier not found or not associated with this report."
            )
        serializer = ReportWithModifierSerializer(
            {"report": report, "modifier": modifier}
        )
        return Response(serializer.data)


class ReportModifierViewSet(viewsets.ModelViewSet):
    queryset = ReportModifier.objects.all()
    serializer_class = ReportModifierSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventGroupViewSet(viewsets.ModelViewSet):
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupSerializer


class RingEventViewSet(viewsets.ModelViewSet):
    queryset = RingEvent.objects.all()
    serializer_class = RingEventSerializer


class BoxEventViewSet(viewsets.ModelViewSet):
    queryset = BoxEvent.objects.all()
    serializer_class = BoxEventSerializer


class GeoEventViewSet(viewsets.ModelViewSet):
    queryset = GeoEvent.objects.all()
    serializer_class = GeoEventSerializer
