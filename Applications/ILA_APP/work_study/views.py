import uuid
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WorkStudyPackage, WorkStudyRoleFeature, WorkStudyStream, WorkStudyCandidate
from .serializers import (
    WorkStudyPackageSerializer,
    WorkStudyCandidateSerializer,
    JDPromotionSerializer
)

class WorkStudyPackageViewSet(viewsets.ModelViewSet):
    """
    CRUD API ViewSet for Work & Study Packages
    """
    queryset = WorkStudyPackage.objects.all().prefetch_related('roles', 'streams')
    serializer_class = WorkStudyPackageSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        pkg_id = data.get('id') or f"WSP-PKG-{uuid.uuid4().hex[:6].upper()}"
        
        package = WorkStudyPackage.objects.create(
            id=pkg_id,
            category=data.get('category', 'work-in-india'),
            category_label=data.get('category_label', 'Work & Study in India'),
            title=data.get('title', ''),
            badge=data.get('badge', 'Featured'),
            stipend=data.get('stipend', '₹15,000 - ₹25,000 / mo'),
            training_duration=data.get('training_duration', '6 Months Initial Training Session'),
            internship_duration=data.get('internship_duration', '6 Months Corporate Pilot'),
            certification=data.get('certification', '1-Year Verified Corporate Certificate'),
            action_text=data.get('action_text', 'Apply Now'),
            description=data.get('description', ''),
            terms_and_conditions=data.get('terms_and_conditions', ''),
            status=data.get('status', 'Active')
        )

        # Save roles / features
        roles = data.get('roles', [])
        for order, r in enumerate(roles):
            WorkStudyRoleFeature.objects.create(
                package=package,
                title=r,
                order=order,
                is_milestone=order < 3
            )

        # Save selectable streams
        streams = data.get('streams', [])
        for s in streams:
            WorkStudyStream.objects.create(
                package=package,
                name=s
            )

        serializer = self.get_serializer(package)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='promote-jd')
    def promote_jd(self, request, pk=None):
        """
        Promote Job Description directly to Marketing Studio and Social Media Ads
        """
        package = self.get_object()
        serializer = JDPromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        campaign_id = f"JD-CMP-{uuid.uuid4().hex[:5].upper()}"
        channels = serializer.validated_data.get('channels')
        target_region = serializer.validated_data.get('target_region')

        # Update package state
        package.promoted_to_marketing = True
        package.marketing_campaign_id = campaign_id
        package.last_promoted_at = timezone.now()
        package.save()

        return Response({
            'success': True,
            'campaign_id': campaign_id,
            'channels': channels,
            'target_region': target_region,
            'message': f"Job Description '{package.title}' successfully pushed to Marketing Studio ({', '.join(channels)})"
        }, status=status.HTTP_200_OK)


class WorkStudyCandidateViewSet(viewsets.ModelViewSet):
    """
    HOD Candidate Intake & Milestone Management ViewSet
    """
    queryset = WorkStudyCandidate.objects.all().select_related('package')
    serializer_class = WorkStudyCandidateSerializer

    @action(detail=True, methods=['post'], url_path='advance-stage')
    def advance_stage(self, request, pk=None):
        candidate = self.get_object()
        new_stage = request.data.get('stage')
        new_progress = request.data.get('progress_pct')

        if new_stage:
            candidate.stage = new_stage
        if new_progress is not None:
            candidate.progress_pct = new_progress
        candidate.save()

        return Response(self.get_serializer(candidate).data, status=status.HTTP_200_OK)
