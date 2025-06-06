from rest_framework import serializers
from api.models.report import Report, ReportModifier
from api.models.job import Job
from api.models.event import Event, EventGroup, RingEvent, BoxEvent, GeoEvent
from django.core.exceptions import ValidationError
import re


def validate_cron(value):
    if value and not re.match(
        r"^[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+$", value
    ):
        raise serializers.ValidationError("Invalid cron syntax")


def validate_latitude(value):
    if not -90 <= value <= 90:
        raise serializers.ValidationError(
            "Latitude must be between -90 and 90 degrees."
        )


def validate_longitude(value):
    if not -180 <= value <= 180:
        raise serializers.ValidationError(
            "Longitude must be between -180 and 180 degrees."
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "description", "is_valid"]


class RingEventSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(validators=[validate_latitude])
    longitude = serializers.FloatField(validators=[validate_longitude])
    radius = serializers.FloatField(min_value=0)

    class Meta:
        model = RingEvent
        fields = [
            "id",
            "name",
            "description",
            "is_valid",
            "latitude",
            "longitude",
            "radius",
        ]


class BoxEventSerializer(serializers.ModelSerializer):
    max_lat = serializers.FloatField(validators=[validate_latitude])
    min_lat = serializers.FloatField(validators=[validate_latitude])
    max_lon = serializers.FloatField(validators=[validate_longitude])
    min_lon = serializers.FloatField(validators=[validate_longitude])

    def validate(self, data):
        if data["max_lat"] <= data["min_lat"]:
            raise serializers.ValidationError("max_lat must be greater than min_lat.")
        if data["max_lon"] <= data["min_lon"]:
            raise serializers.ValidationError("max_lon must be greater than min_lon.")
        return data

    class Meta:
        model = BoxEvent
        fields = [
            "id",
            "name",
            "description",
            "is_valid",
            "max_lat",
            "min_lat",
            "max_lon",
            "min_lon",
        ]


class GeoEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoEvent
        fields = [
            "id",
            "name",
            "description",
            "is_valid",
            "country",
            "area",
            "subarea",
            "subarea2",
        ]


class EventGroupSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    event_ids = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), many=True, write_only=True, source="events"
    )

    class Meta:
        model = EventGroup
        fields = ["id", "name", "events", "event_ids", "created", "updated"]
