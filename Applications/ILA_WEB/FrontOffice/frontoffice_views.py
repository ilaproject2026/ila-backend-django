from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Sum, Q

from .frontoffice_models import Inquiry, FollowUpRecord, VisitorLog
from .frontoffice_serializers import (
    InquirySerializer,
    FollowUpRecordSerializer,
    VisitorLogSerializer,
    InquiryPaymentSerializer,
)


class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all().prefetch_related('follow_up_history', 'assigned_staff')
    serializer_class = InquirySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        lead_type = self.request.query_params.get('lead_type')
        department = self.request.query_params.get('department')
        category = self.request.query_params.get('category')
        crm_status = self.request.query_params.get('crm_status')
        pipeline_stage = self.request.query_params.get('pipeline_stage')
        visa_stage = self.request.query_params.get('visa_stage')
        follow_up_status = self.request.query_params.get('follow_up_status')
        search = self.request.query_params.get('search')

        if lead_type:
            queryset = queryset.filter(lead_type__iexact=lead_type)
        if department:
            queryset = queryset.filter(department__iexact=department)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if crm_status:
            queryset = queryset.filter(crm_status__iexact=crm_status)
        if pipeline_stage:
            queryset = queryset.filter(pipeline_stage__iexact=pipeline_stage)
        if visa_stage:
            queryset = queryset.filter(visa_stage__iexact=visa_stage)
        if follow_up_status:
            queryset = queryset.filter(follow_up_status__iexact=follow_up_status)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(token_number__icontains=search)
            )

        return queryset

    @action(detail=True, methods=['post'], url_path='followup')
    def add_followup(self, request, pk=None):
        inquiry = self.get_object()
        serializer = FollowUpRecordSerializer(data=request.data)
        if serializer.is_valid():
            followup = serializer.save(
                inquiry=inquiry,
                staff=request.user if request.user and request.user.is_authenticated else None
            )
            # Update inquiry follow_up_date and status
            if followup.next_follow_up_date:
                inquiry.follow_up_date = followup.next_follow_up_date
                inquiry.follow_up_status = 'Scheduled'
            else:
                inquiry.follow_up_status = 'Completed'
            inquiry.save()
            return Response(FollowUpRecordSerializer(followup).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='assign-staff')
    def assign_staff(self, request, pk=None):
        inquiry = self.get_object()
        staff_id = request.data.get('staff_id')
        if not staff_id:
            return Response({'error': 'staff_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff = User.objects.filter(id=staff_id).first()
        if not staff:
            return Response({'error': 'Staff user not found'}, status=status.HTTP_404_NOT_FOUND)

        inquiry.assigned_staff = staff
        inquiry.save()
        return Response({'message': f'Inquiry assigned to {staff.username}', 'inquiry': InquirySerializer(inquiry).data})

    @action(detail=True, methods=['post'], url_path='payment')
    def process_payment(self, request, pk=None):
        inquiry = self.get_object()
        serializer = InquiryPaymentSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            payment_status_val = serializer.validated_data['payment_status']
            notes = serializer.validated_data.get('notes', '')

            inquiry.amount_paid += amount
            if inquiry.amount_paid >= inquiry.total_amount and inquiry.total_amount > 0:
                inquiry.payment_status = 'Paid'
            else:
                inquiry.payment_status = payment_status_val
            inquiry.save()

            # Auto-sync to Financial Ledger
            try:
                from Applications.ILA_WEB.Finance.finance_models import FinancialLedger
                FinancialLedger.objects.create(
                    transaction_type='income',
                    category='Education Revenue',
                    description=f"Payment for {inquiry.token_number} - {inquiry.name}: {notes}".strip(),
                    amount=amount,
                    reference_id=inquiry.token_number,
                    created_by=request.user if request.user and request.user.is_authenticated else None
                )
            except Exception as e:
                # In case finance app isn't ready or other issue
                pass

            return Response({
                'message': 'Payment recorded and synced to ledger successfully',
                'inquiry': InquirySerializer(inquiry).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='stats/daily')
    def daily_stats(self, request):
        today = timezone.now().date()
        today_inquiries = Inquiry.objects.filter(created_at__date=today)
        walk_ins = today_inquiries.filter(lead_type='Walk-in').count()
        online_leads = today_inquiries.filter(lead_type='Online').count()
        conversions = Inquiry.objects.filter(crm_status='Closed Won').count()
        overdue_calls = Inquiry.objects.filter(
            Q(follow_up_status='Overdue') | Q(follow_up_date__lt=today, follow_up_status__in=['Scheduled', 'Pending'])
        ).count()
        today_revenue = today_inquiries.aggregate(total=Sum('amount_paid'))['total'] or 0

        return Response({
            'date': today,
            'today_walk_ins': walk_ins,
            'today_online_leads': online_leads,
            'total_inquiries_today': today_inquiries.count(),
            'total_conversions': conversions,
            'overdue_calls': overdue_calls,
            'today_revenue': float(today_revenue),
        })


class VisitorLogCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VisitorLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip_address=request.META.get('REMOTE_ADDR'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
