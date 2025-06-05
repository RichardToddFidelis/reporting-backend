# reporting-backend/api/models/report.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .event import EventGroup
import re
from django.core.validators import MinValueValidator, MaxValueValidator

def validate_cron(value):
    if not re.match(
        r"^[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+$",
        value
    ):
        raise ValidationError("Invalid cron syntax")

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    peril = models.CharField(max_length=100)
    dr = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=1.0
    )
    event_groups = models.ManyToManyField(
        EventGroup,
        related_name="reports",
        db_table="_jt_reports_eventgroups",
        blank=True,
    )
    cron = models.CharField(
        max_length=50, blank=True, null=True, validators=[validate_cron]
    )
    cob = models.CharField(max_length=50, null=True)
    loss_perspective = models.CharField(max_length=20)
    is_apply_calibration = models.BooleanField(default=True)
    is_apply_inflation = models.BooleanField(default=True)
    is_tag_outwards_ptns = models.BooleanField(default=False)
    is_location_breakout = models.BooleanField(default=False)
    is_ignore_missing_lat_lon = models.BooleanField(default=True)
    location_breakout_max_events = models.IntegerField(default=500000)
    location_breakout_max_locations = models.IntegerField(default=1000000)
    priority = models.CharField(max_length=50, default="AboveNormal")
    ncores = models.IntegerField(default=24)
    gross_node_id = models.IntegerField(null=True)
    net_node_id = models.IntegerField(null=True)
    rollup_context_id = models.IntegerField(null=True)
    dynamic_ring_loss_threshold = models.IntegerField(default=5000000)
    blast_radius = models.FloatField(default=50, null=True)
    no_overlap_radius = models.FloatField(null=True)
    is_valid = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report {self.id}"

    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "reports"
        app_label='api'

class ReportModifier(models.Model):
    id = models.AutoField(primary_key=True)
    as_at_date = models.DateField(null=True)
    fx_date = models.DateField(null=True)
    reports = models.ManyToManyField(
        Report,
        related_name="modifiers",
        db_table="_jt_report_modifiers_reports",
        blank=True,
    )

    @property
    def quarter(self):
        if not self.as_at_date:
            return None
        month = self.as_at_date.month
        return (month - 3) // 4

    @property
    def year(self):
        return self.as_at_date.year if self.as_at_date else None

    @property
    def month(self):
        return self.as_at_date.month if self.as_at_date else None

    @property
    def day(self):
        return self.as_at_date.day if self.as_at_date else None

    class Meta:
        db_table = "report_modifiers"
        app_label = "api"
