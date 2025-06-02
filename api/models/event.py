from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Validators for latitude and longitude


def validate_latitude(value):
    if not -90 <= value <= 90:
        raise ValidationError("Latitude must be between -90 and 90 degrees.")


def validate_longitude(value):
    if not -180 <= value <= 180:
        raise ValidationError("Longitude must be between -180 and 180 degrees.")


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)

    class Meta:
        db_table = "events"


class EventGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    events = models.ManyToManyField(
        Event,
        related_name="event_groups",
        db_table="_jt_eventgroup_events",  # Specify junction table name directly
    )
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)


class RingEvent(Event):
    latitude = models.FloatField(
        validators=[validate_latitude], null=False, blank=False
    )
    longitude = models.FloatField(
        validators=[validate_longitude], null=False, blank=False
    )
    radius = models.FloatField(
        validators=[MinValueValidator(0)], null=False, blank=False
    )


class BoxEvent(Event):
    max_lat = models.FloatField(validators=[validate_latitude], null=False, blank=False)
    min_lat = models.FloatField(validators=[validate_latitude], null=False, blank=False)
    max_lon = models.FloatField(
        validators=[validate_longitude], null=False, blank=False
    )
    min_lon = models.FloatField(
        validators=[validate_longitude], null=False, blank=False
    )

    def clean(self):
        if self.max_lat <= self.min_lat:
            raise ValidationError("max_lat must be greater than min_lat.")
        if self.max_lon <= self.min_lon:
            raise ValidationError("max_lon must be greater than min_lon.")


class GeoEvent(Event):
    country = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    subarea = models.CharField(max_length=255, null=True, blank=True)
    subarea2 = models.CharField(max_length=255, null=True, blank=True)
