import logging
from .services.smtp_service import dispatch_batch_campaign
from .services.gemini_client import gemini_client
from .models import LibraryCourse, CourseChapter, GenerationJob

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:
    # Fallback decorator if celery is not installed
    def shared_task(*args, **kwargs):
        def decorator(func):
            def wrapper(*a, **kw):
                return func(*a, **kw)
            wrapper.delay = wrapper
            return wrapper
        return decorator if (args and callable(args[0])) else decorator


@shared_task(bind=True, rate_limit='30/m')
def send_bulk_outreach_task(self, campaign_payload):
    """
    Asynchronous Celery task for pacing bulk outreach campaigns.
    """
    logger.info("[Celery Task] Starting bulk outreach dispatch...")
    result = dispatch_batch_campaign(campaign_payload)
    return result


@shared_task(bind=True)
def generate_autonomous_course_task(self, job_id, course_id, topic, chapter_count=4, target_audience=""):
    """
    Asynchronously generates a multi-chapter course using Gemini AI,
    updating the GenerationJob progress along the way.
    """
    job = GenerationJob.objects.filter(id=job_id).first()
    if job:
        job.status = 'processing'
        job.progress = 10
        job.save()

    try:
        course = LibraryCourse.objects.filter(id=course_id).first()
        if not course:
            course = LibraryCourse.objects.create(
                id=course_id,
                title=f"Autonomous Course: {topic}",
                overview=f"Comprehensive {chapter_count}-chapter master curriculum on {topic}.",
                target_audience=target_audience,
                total_chapters=chapter_count
            )

        for i in range(1, chapter_count + 1):
            prompt = (
                f"Author Chapter {i} of {chapter_count} for the course '{topic}'. "
                f"Target Audience: {target_audience or 'General Students'}. "
                f"Provide Chapter Title, 3-sentence Summary, Key Subtopics list, and 300-word comprehensive deep-dive Content."
            )
            res = gemini_client.generate_content(prompt, product_type="course_creator")
            content = res.get('content', '')

            # Save or update chapter
            chap_id = f"chap_{course.id}_{i}"
            CourseChapter.objects.update_or_create(
                id=chap_id,
                course=course,
                defaults={
                    'chapter_number': i,
                    'title': f"Module {i}: {topic} Core Essentials",
                    'summary': f"Key learning objectives and competencies for Module {i}.",
                    'content': content,
                    'is_completed': False,
                    'sub_topics': [f"{topic} Fundamental Concepts", f"Practical Implementation {i}", f"Case Study & Assessment"]
                }
            )
            if job:
                job.progress = int(10 + (i / chapter_count) * 85)
                job.save()

        if job:
            job.status = 'completed'
            job.progress = 100
            job.result = {'courseId': course.id, 'title': course.title}
            job.save()

        return {'status': 'completed', 'courseId': course.id}
    except Exception as exc:
        logger.error(f"[Generate Autonomous Course Task Failed] {exc}")
        if job:
            job.status = 'failed'
            job.error_message = str(exc)
            job.save()
        return {'status': 'failed', 'error': str(exc)}
