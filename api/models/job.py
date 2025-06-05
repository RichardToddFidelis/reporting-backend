from django.db import models
from django.utils import timezone
from .report import Report, ReportModifier


class Job(models.Model):
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="jobs")
    report_modifier = models.ForeignKey(
        ReportModifier,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.id} for Report {self.report_id}"

    class Meta:
        db_table = "jobs"
