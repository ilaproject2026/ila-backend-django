from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_automated_welcome_email(inquiry_id):
    from .models import Inquiry
    try:
        inquiry = Inquiry.objects.get(id=inquiry_id)
        send_mail(
            subject="Welcome to ILA Academy Global — Your Application Intake Confirmed",
            message=(
                f"Hello {inquiry.name},\n\n"
                f"Your application for {inquiry.category} ({inquiry.course}) has been received and "
                f"synchronized with our HOD Desk.\n\n"
                f"Your dedicated 'ILA's With You' account has been provisioned.\n\n"
                f"Reference Token: {inquiry.token_number or inquiry.id}\n"
                f"Pipeline Stage: {inquiry.pipeline_stage}\n\n"
                f"Best Regards,\n"
                f"ILA Academy Global Admissions Team"
            ),
            from_email="admissions@ilaglobal.edu",
            recipient_list=[inquiry.email],
            fail_silently=True,
        )
        logger.info(f"Sent welcome email to {inquiry.email} for inquiry {inquiry_id}")
    except Exception as e:
        logger.error(f"Failed to send welcome email for inquiry {inquiry_id}: {e}")


@shared_task
def trigger_ai_preliminary_interview(application_id):
    from .models import WorkStudyApplication
    try:
        app = WorkStudyApplication.objects.get(id=application_id)
        # Generate custom AI agent interview link
        app.ai_preliminary_interview_link = f"https://interview.ilaglobal.edu/session/{app.id}"
        app.ai_interview_status = 'Completed'
        app.save(update_fields=['ai_preliminary_interview_link', 'ai_interview_status'])
        logger.info(f"Generated AI interview link for application {application_id}")
    except Exception as e:
        logger.error(f"Error triggering AI interview for application {application_id}: {e}")
