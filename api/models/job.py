from django.db import models
from django.utils import timezone
from .report import Report


class Job(models.Model):
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="jobs")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.id} for Report {self.report_id}"

    class Meta:
        db_table = "jobs"
