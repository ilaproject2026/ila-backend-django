from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Sum

from .hrms_models import (
    StaffProfile,
    AttendanceLog,
    HRCandidate,
    EnterpriseTask,
    ApprovalRequest,
)
from .hrms_serializers import (
    StaffProfileSerializer,
    AttendanceLogSerializer,
    HRCandidateSerializer,
    EnterpriseTaskSerializer,
    ApprovalRequestSerializer,
)


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all().select_related('user')
    serializer_class = StaffProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.query_params.get('department')
        status_val = self.request.query_params.get('status')
        if department:
            queryset = queryset.filter(department__iexact=department)
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        return queryset


class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all().select_related('staff__user')
    serializer_class = AttendanceLogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get('date')
        staff_id = self.request.query_params.get('staff')
        if date:
            queryset = queryset.filter(date=date)
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        employee_id = request.data.get('employee_id')
        status_val = request.data.get('status', 'Present')
        now_time = timezone.now().strftime('%H:%M')
        today = timezone.now().date()

        staff = StaffProfile.objects.filter(employee_id=employee_id).first()
        if not staff:
            return Response({'error': 'Staff profile with this employee_id not found'}, status=status.HTTP_404_NOT_FOUND)

        log, created = AttendanceLog.objects.get_or_create(
            staff=staff,
            date=today,
            defaults={'check_in_time': now_time, 'status': status_val}
        )
        if not created and not log.check_out_time:
            log.check_out_time = now_time
            log.save()

        return Response(AttendanceLogSerializer(log).data, status=status.HTTP_200_OK)


class HRCandidateViewSet(viewsets.ModelViewSet):
    queryset = HRCandidate.objects.all()
    serializer_class = HRCandidateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        stage = self.request.query_params.get('stage')
        status_val = self.request.query_params.get('status')
        department = self.request.query_params.get('department')
        if stage:
            queryset = queryset.filter(stage__iexact=stage)
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        if department:
            queryset = queryset.filter(department__iexact=department)
        return queryset

    @action(detail=True, methods=['patch'], url_path='stage')
    def update_stage(self, request, pk=None):
        candidate = self.get_object()
        stage = request.data.get('stage')
        status_val = request.data.get('status')
        if stage:
            candidate.stage = stage
        if status_val:
            candidate.status = status_val
        candidate.save()
        return Response(HRCandidateSerializer(candidate).data)


class EnterpriseTaskViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseTask.objects.all().select_related('assigned_staff')
    serializer_class = EnterpriseTaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_val = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        dept = self.request.query_params.get('department')
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        if priority:
            queryset = queryset.filter(priority__iexact=priority)
        if dept:
            queryset = queryset.filter(assigned_to_dept__iexact=dept)
        return queryset


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all().select_related('requested_by', 'reviewed_by')
    serializer_class = ApprovalRequestSerializer
    permission_classes = [AllowAny]


class PayrollSyncView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        total_salary = StaffProfile.objects.filter(status='Active').aggregate(total=Sum('monthly_salary'))['total'] or 0
        now = timezone.now()
        ref_id = f"PAYROLL-{now.strftime('%Y%m')}"

        try:
            from Applications.ILA_WEB.Finance.finance_models import FinancialLedger
            entry, created = FinancialLedger.objects.get_or_create(
                reference_id=ref_id,
                defaults={
                    'transaction_type': 'expense',
                    'category': 'Payroll Sync',
                    'description': f"Monthly Staff Payroll Sync for {now.strftime('%B %Y')}",
                    'amount': total_salary,
                    'created_by': request.user if request.user and request.user.is_authenticated else None
                }
            )
            return Response({
                'message': 'Payroll synced to finance ledger successfully',
                'reference_id': ref_id,
                'total_amount': float(total_salary),
                'created': created
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
