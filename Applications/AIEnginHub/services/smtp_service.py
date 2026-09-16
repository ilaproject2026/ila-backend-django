import time
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models import OutreachStatusLog, TieupLead

logger = logging.getLogger(__name__)


def verify_smtp_connection(host: str, port: int, user: str, password: str, secure: bool = False):
    """
    Validates SMTP credentials with upstream mail server.
    """
    try:
        if secure or port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
                server.login(user, password)
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls()
                server.login(user, password)

        return {
            "success": True,
            "connected": True,
            "message": f"Successfully verified SMTP connection to {host}:{port} as {user}"
        }
    except Exception as exc:
        logger.error(f"[SMTP Verification Failed] {exc}")
        return {
            "success": False,
            "connected": False,
            "error": str(exc),
            "errorType": "SMTP_HANDSHAKE_FAILED"
        }


def send_single_email(host: str, port: int, sender_email: str, app_password: str,
                      recipient_email: str, subject: str, content: str,
                      lead_id=None, institution_name: str = "", secure: bool = False):
    """
    Dispatches a single email and records an OutreachStatusLog entry.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        if secure or port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=12) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=12) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)

        lead_obj = None
        if lead_id:
            lead_obj = TieupLead.objects.filter(id=lead_id).first()

        log = OutreachStatusLog.objects.create(
            lead=lead_obj,
            institution_name=institution_name or (lead_obj.name if lead_obj else recipient_email),
            recipient_email=recipient_email,
            sender_email=sender_email,
            subject=subject,
            status='delivered'
        )

        return {"success": True, "logId": str(log.id), "status": "delivered"}
    except Exception as exc:
        logger.error(f"[Send Single Email Failed] {exc}")
        return {"success": False, "error": str(exc), "status": "failed"}


def dispatch_batch_campaign(campaign_payload: dict):
    """
    Iteratively sends outreach emails with anti-spam rate delays (300ms - 800ms)
    and variable interpolation.
    """
    sender_email = campaign_payload.get('senderEmail') or campaign_payload.get('sender_email')
    app_password = campaign_payload.get('appPassword') or campaign_payload.get('app_password')
    host = campaign_payload.get('host', 'smtp.gmail.com')
    port = int(campaign_payload.get('port', 587))
    secure = bool(campaign_payload.get('secure', port == 465))
    leads = campaign_payload.get('leads', [])
    subject_tmpl = campaign_payload.get('subjectTemplate') or campaign_payload.get('subject_template', '')
    body_tmpl = campaign_payload.get('bodyTemplate') or campaign_payload.get('body_template', '')
    delay_ms = int(campaign_payload.get('delayMs', 500))

    delivered_count = 0
    failed_count = 0
    errors = []

    try:
        server_cls = smtplib.SMTP_SSL if (secure or port == 465) else smtplib.SMTP
        server = server_cls(host, port, timeout=15)
        if not (secure or port == 465):
            server.starttls()
        server.login(sender_email, app_password)

        for lead in leads:
            try:
                recipient = lead.get('contactEmail') or lead.get('contact_email')
                lead_name = lead.get('name', 'Institution')
                lead_id = lead.get('id')

                if not recipient:
                    continue

                subj = subject_tmpl.replace('{{lead.name}}', lead_name).replace('{{name}}', lead_name)
                content = body_tmpl.replace('{{lead.name}}', lead_name).replace('{{name}}', lead_name)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = subj
                msg.attach(MIMEText(content, 'plain'))

                server.send_message(msg)
                delivered_count += 1

                lead_obj = TieupLead.objects.filter(id=lead_id).first() if lead_id else None
                OutreachStatusLog.objects.create(
                    lead=lead_obj,
                    institution_name=lead_name,
                    recipient_email=recipient,
                    sender_email=sender_email,
                    subject=subj,
                    status='delivered'
                )

                time.sleep(delay_ms / 1000.0)
            except Exception as e_inner:
                failed_count += 1
                errors.append(str(e_inner))

        server.quit()
    except Exception as e_outer:
        return {"success": False, "error": str(e_outer), "delivered": delivered_count, "failed": failed_count}

    return {
        "success": True,
        "delivered": delivered_count,
        "failed": failed_count,
        "errors": errors[:5]
    }
