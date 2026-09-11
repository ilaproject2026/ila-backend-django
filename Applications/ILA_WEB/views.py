from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    FranchisePartner, Inquiry, FollowUpRecord,
    PartnerInstitution, TieUpOutreachLog, MarketingCampaign,
    FieldVisitLog, DepartmentMeeting, RewardProfile, RewardTransaction,
    WorkStudyApplication, VisaRequirementRule, SettlementServiceRequest,
    EnterpriseTask, AttendanceLog, ApprovalRequest
)
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, FranchisePartnerSerializer,
    InquirySerializer, FollowUpRecordSerializer, PartnerInstitutionSerializer,
    TieUpOutreachLogSerializer, MarketingCampaignSerializer, FieldVisitLogSerializer,
    DepartmentMeetingSerializer, RewardProfileSerializer, RewardTransactionSerializer,
    WorkStudyApplicationSerializer, VisaRequirementRuleSerializer,
    SettlementServiceRequestSerializer, EnterpriseTaskSerializer,
    AttendanceLogSerializer, ApprovalRequestSerializer
)
from .permissions import IsSuperAdminUser, IsCEOOrGM, IsDepartmentHOD, HasBiometricAuthorization

User = get_user_model()


# ==============================================================================
# AUTHENTICATION ENDPOINTS
# ==============================================================================
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        role = request.data.get('role', 'student')
        department = request.data.get('department', '')
        phone = request.data.get('phone', '')

        if not email or not password:
            return Response(
                {'detail': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'User with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse names
        if full_name and not (first_name or last_name):
            parts = full_name.strip().split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            department=department
        )
        if hasattr(user, 'fullname') and full_name:
            user.fullname = full_name
            user.save(update_fields=['fullname'])

        # Dual-account provisioning in Rewards Club (Part 2 & 6)
        RewardProfile.objects.create(
            user=user,
            consultant_id=f"ILA-JC-{user.id:04d}",
            tier='Junior Consultant',
            active_points=100
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ==============================================================================
# CORE ENTERPRISE VIEWSETS
# ==============================================================================
class StaffViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'department', 'status', 'is_biometric_authorized']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'hr_issued_id']


class FranchiseViewSet(viewsets.ModelViewSet):
    queryset = FranchisePartner.objects.select_related('created_by').all().order_by('-created_at')
    serializer_class = FranchisePartnerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['region', 'is_active']
    search_fields = ['name', 'email', 'franchise_token', 'region']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.prefetch_related('follow_ups').all().order_by('-created_at')
    serializer_class = InquirySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'payment_status', 'crm_status', 'target_country', 'target_keyword', 'department']
    search_fields = ['name', 'email', 'phone', 'course', 'target_keyword', 'token_number']
    ordering_fields = ['created_at', 'updated_at', 'name', 'ai_score', 'category', 'crm_status']

    def get_permissions(self):
        # Public users can submit an intake application without logging in
        if self.action == 'create':
            return [permissions.AllowAny()]
        # All administrative CRM actions require authentication
        return [permissions.IsAuthenticated()]


class FollowUpRecordViewSet(viewsets.ModelViewSet):
    queryset = FollowUpRecord.objects.select_related('inquiry').all().order_by('-created_at')
    serializer_class = FollowUpRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['inquiry', 'channel', 'outcome']
    search_fields = ['staff_name', 'notes']


class PartnerInstitutionViewSet(viewsets.ModelViewSet):
    queryset = PartnerInstitution.objects.annotate(outreach_logs_count=Count('outreach_logs')).all().order_by('-last_updated')
    serializer_class = PartnerInstitutionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'country', 'status']
    search_fields = ['name', 'city', 'contact_person', 'email', 'target_criteria']


class TieUpOutreachLogViewSet(viewsets.ModelViewSet):
    queryset = TieUpOutreachLog.objects.select_related('partner', 'dispatched_by').all().order_by('-dispatched_at')
    serializer_class = TieUpOutreachLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['partner', 'is_dispatched']
    search_fields = ['subject', 'generated_proposal_text', 'response_notes']


class MarketingCampaignViewSet(viewsets.ModelViewSet):
    queryset = MarketingCampaign.objects.all().order_by('-created_at')
    serializer_class = MarketingCampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'target_geography']
    search_fields = ['name', 'channel']


class FieldVisitLogViewSet(viewsets.ModelViewSet):
    queryset = FieldVisitLog.objects.select_related('logged_by').all().order_by('-visit_date')
    serializer_class = FieldVisitLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['institution_visited', 'contact_person', 'location', 'summary']


class DepartmentMeetingViewSet(viewsets.ModelViewSet):
    queryset = DepartmentMeeting.objects.all().order_by('-date')
    serializer_class = DepartmentMeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'status']
    search_fields = ['title', 'agenda', 'attendees']


class RewardProfileViewSet(viewsets.ModelViewSet):
    queryset = RewardProfile.objects.select_related('user').prefetch_related('transactions').all().order_by('-lifetime_points')
    serializer_class = RewardProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tier', 'work_certificate_issued']
    search_fields = ['consultant_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name']


class RewardTransactionViewSet(viewsets.ModelViewSet):
    queryset = RewardTransaction.objects.select_related('profile', 'profile__user').all().order_by('-timestamp')
    serializer_class = RewardTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['profile', 'milestone_type']
    search_fields = ['description', 'reference_inquiry_id']


class WorkStudyApplicationViewSet(viewsets.ModelViewSet):
    queryset = WorkStudyApplication.objects.all().order_by('-created_at')
    serializer_class = WorkStudyApplicationSerializer
    permission_classes = [permissions.AllowAny]  # Allow students/candidates to apply publicly
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['track', 'ai_interview_status', 'is_onboarded_to_dept']
    search_fields = ['candidate_name', 'email', 'phone', 'sub_domain']


class VisaRequirementRuleViewSet(viewsets.ModelViewSet):
    queryset = VisaRequirementRule.objects.all().order_by('country')
    serializer_class = VisaRequirementRuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country', 'visa_type']
    search_fields = ['country', 'visa_type', 'primary_authority']


class SettlementServiceViewSet(viewsets.ModelViewSet):
    queryset = SettlementServiceRequest.objects.select_related('assigned_coordinator').all().order_by('-arrival_date')
    serializer_class = SettlementServiceRequestSerializer
    permission_classes = [permissions.AllowAny]  # Public service request intake
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['target_country', 'status']
    search_fields = ['candidate_name', 'email']


class EnterpriseTaskViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseTask.objects.all().order_by('-created_at')
    serializer_class = EnterpriseTaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['assigned_to_dept', 'status', 'priority']
    search_fields = ['title', 'description']


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all().order_by('-id')
    serializer_class = AttendanceLogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'date']
    search_fields = ['staff_id', 'staff_name']


class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all().order_by('-id')
    serializer_class = ApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'status', 'type']
    search_fields = ['requested_by', 'description']


# Live Consultant Chat views
from .IlaConsultant.views import ConsultantChatAPIView, ConsultantSessionViewSet

