import uuid
from django.db import models
from django.conf import settings


def generate_inquiry_id():
    return f"inq-{uuid.uuid4().hex[:8]}"


def generate_followup_id():
    return f"FL-{uuid.uuid4().hex[:6]}"


# Forward canonical models from blueprint
from Applications.ILA_WEB.models import Inquiry, FollowUpRecord  # noqa: E402


class VisitorLog(models.Model):
    page = models.CharField(max_length=255)
    time_spent_seconds = models.IntegerField(default=0)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.page} ({self.time_spent_seconds}s) at {self.timestamp}"
