from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from Applications.AIEnginHub.models import (
    CourseCategory, LibraryCourse, CourseChapter, ChatSession, ChatMessage,
    TieupLead, TieupPolicy, OutreachStatusLog
)


class AIEnginHubApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Category
        self.category = CourseCategory.objects.create(
            id="cat_tech",
            name="Technology & Data",
            department="Engineering",
            color="#3B82F6"
        )

        # Create Course with Chapters
        self.course = LibraryCourse.objects.create(
            id="test_course_01",
            title="Django DRF Masterclass",
            category="Technology & Data",
            total_chapters=2,
            is_permanent=True,
            locked=True
        )
        self.chapter1 = CourseChapter.objects.create(
            id="chap_test_1",
            course=self.course,
            chapter_number=1,
            title="Introduction to DRF",
            summary="Basics of ViewSets & Serializers",
            is_completed=False,
            sub_topics=["Setup", "Routing"]
        )
        self.chapter2 = CourseChapter.objects.create(
            id="chap_test_2",
            course=self.course,
            chapter_number=2,
            title="Advanced Async Pipelines",
            summary="Celery & Redis",
            is_completed=False,
            sub_topics=["Tasks", "Pacing"]
        )

        # Create Session & Message
        self.session = ChatSession.objects.create(
            id="session_test_01",
            title="Curriculum Planning Session",
            product_type="course_creator"
        )
        self.message = ChatMessage.objects.create(
            id="msg_test_01",
            session=self.session,
            role="user",
            content="Generate 4 chapters on Cloud Computing"
        )

        # Create Tieup Lead & Policy
        self.lead = TieupLead.objects.create(
            id="lead_test_01",
            name="University of Oxford",
            category="Public Research",
            country="United Kingdom",
            location_main="Oxford, UK",
            contact_person="Prof. John Doe",
            contact_title="Dean",
            contact_email="dean@oxford.ac.uk",
            compatibility_score=95
        )
        self.policy = TieupPolicy.objects.create(
            id="global_policy",
            min_commission_percent=15.0,
            target_commission_percent=20.0
        )

    def test_health_check(self):
        res = self.client.get('/api/v1/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('status'), 'healthy')

    def test_dashboard_stats(self):
        res = self.client.get('/api/v1/dashboard/stats/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('totalCourses', res.data)
        self.assertEqual(res.data['totalCourses'], 1)

    def test_courses_list_and_detail(self):
        res = self.client.get('/api/v1/courses/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results', res.data)), 1)

        res_detail = self.client.get(f'/api/v1/courses/{self.course.id}/')
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data['title'], "Django DRF Masterclass")
        self.assertEqual(len(res_detail.data['chapters']), 2)

    def test_course_toggle_chapter(self):
        res = self.client.post(f'/api/v1/courses/{self.course.id}/toggle-chapter/', {'chapterId': self.chapter1.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['isCompleted'])

    def test_permanent_courses_download(self):
        res = self.client.post(f'/api/v1/permanent-courses/{self.course.id}/download/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['downloadCount'], 1)

    def test_chat_session_actions(self):
        # Update title
        res_title = self.client.post(f'/api/v1/sessions/{self.session.id}/title/', {'title': 'Updated Session Title'}, format='json')
        self.assertEqual(res_title.status_code, status.HTTP_200_OK)
        self.assertEqual(res_title.data['session']['title'], 'Updated Session Title')

        # Toggle Pin
        res_pin = self.client.post(f'/api/v1/sessions/{self.session.id}/pin/')
        self.assertEqual(res_pin.status_code, status.HTTP_200_OK)
        self.assertTrue(res_pin.data['isPinned'])

    def test_tieup_lead_partner_toggle(self):
        res = self.client.post(f'/api/v1/tieup-leads/{self.lead.id}/partner/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['isPartner'])

    def test_tieup_policy_get(self):
        res = self.client.get('/api/v1/tieup-policies/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('id'), 'global_policy')

    def test_ai_generate_proxy(self):
        payload = {
            'prompt': 'Provide a summary of German Student Visa Requirements',
            'productType': 'visa_doc_analyzer'
        }
        res = self.client.post('/api/v1/ai/generate/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('content', res.data)
        self.assertIn('model', res.data)

    def test_course_docx_export(self):
        res = self.client.get(f'/api/v1/courses/{self.course.id}/export-docx/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
