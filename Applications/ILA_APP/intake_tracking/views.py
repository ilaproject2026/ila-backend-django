from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import DepartmentInquiry, FollowUpAutoTriggerRule, SocialMediaCampaign
from .serializers import (
    DepartmentInquirySerializer,
    FollowUpAutoTriggerRuleSerializer,
    SocialMediaCampaignSerializer,
)


class DepartmentInquiryViewSet(viewsets.ModelViewSet):
    queryset = DepartmentInquiry.objects.all().order_by("-created_at")
    serializer_class = DepartmentInquirySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        department = self.request.query_params.get("department")
        status_val = self.request.query_params.get("status")
        if department and department != "All":
            qs = qs.filter(department__iexact=department)
        if status_val and status_val != "All":
            qs = qs.filter(status=status_val)
        return qs


class FollowUpAutoTriggerRuleViewSet(viewsets.ModelViewSet):
    queryset = FollowUpAutoTriggerRule.objects.all().order_by("delay_hours")
    serializer_class = FollowUpAutoTriggerRuleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        department = self.request.query_params.get("department")
        if department and department != "All":
            qs = qs.filter(department__iexact=department)
        return qs

    @action(detail=True, methods=["post"], url_path="simulate-execution")
    def simulate_execution(self, request, pk=None):
        trigger = self.get_object()
        trigger.execution_count += 1
        trigger.last_triggered = timezone.now()
        trigger.save()
        return Response({
            "success": True,
            "trigger_name": trigger.trigger_name,
            "execution_count": trigger.execution_count,
            "channel": trigger.channel,
            "dispatched_at": trigger.last_triggered,
        })


class SocialMediaCampaignViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaCampaign.objects.all().order_by("-scheduled_at")
    serializer_class = SocialMediaCampaignSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        department = self.request.query_params.get("department")
        if department and department != "All":
            qs = qs.filter(department__iexact=department)
        return qs

    @action(detail=True, methods=["post"], url_path="broadcast-live")
    def broadcast_live(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "Published"
        campaign.published_at = timezone.now()
        campaign.reach_count += 2400
        campaign.clicks_count += 180
        campaign.save()
        return Response({
            "success": True,
            "campaign_id": campaign.id,
            "status": "Published",
            "published_at": campaign.published_at,
            "estimated_reach": campaign.reach_count,
        })
