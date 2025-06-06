from rest_framework import serializers
from api.models.report import Report, ReportModifier
from api.models.job import Job
from api.models.event import Event, EventGroup, RingEvent, BoxEvent, GeoEvent
from django.core.exceptions import ValidationError
import re


class ReportModifierSerializer(serializers.ModelSerializer):
    quarter = serializers.ReadOnlyField()
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    day = serializers.ReadOnlyField()

    class Meta:
        model = ReportModifier
        fields = ["id", "as_at_date", "fx_date", "quarter", "year", "month", "day"]


class ReportSerializer(serializers.ModelSerializer):
    event_groups = serializers.PrimaryKeyRelatedField(
        queryset=EventGroup.objects.all(), many=True
    )
    cron = serializers.CharField(
        max_length=50, allow_blank=True, allow_null=True, validators=[validate_cron]
    )
    modifiers = ReportModifierSerializer(many=True, read_only=True, source="modifiers")

    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "peril",
            "dr",
            "event_groups",
            "cron",
            "cob",
            "loss_perspective",
            "is_apply_calibration",
            "is_apply_inflation",
            "is_tag_outwards_ptns",
            "is_location_breakout",
            "is_ignore_missing_lat_lon",
            "location_breakout_max_events",
            "location_breakout_max_locations",
            "priority",
            "ncores",
            "gross_node_id",
            "net_node_id",
            "rollup_context_id",
            "dynamic_ring_loss_threshold",
            "blast_radius",
            "no_overlap_radius",
            "is_valid",
            "created",
            "updated",
            "modifiers",
        ]


class ReportWithModifierSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    modifier = ReportModifierSerializer()

    class Meta:
        model = Job
        fields = ["report", "modifier"]
