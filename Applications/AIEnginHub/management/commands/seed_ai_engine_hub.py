from django.core.management.base import BaseCommand
from Applications.AIEnginHub.models import (
    CourseCategory, TieupPolicy, AIProductPreset, TieupLead, LibraryCourse, CourseChapter
)
from Applications.AIEnginHub.services.gemini_client import PROMPT_REGISTRY


class Command(BaseCommand):
    help = 'Seeds initial data for ILA AI Engine Hub, Course Creator & Tie-Up CRM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding ILA AI Engine Hub defaults..."))

        # 1. Course Categories
        categories = [
            {"id": "cat_cs_ai", "name": "Computer Science & AI", "department": "School of Technology", "color": "#3B82F6", "description": "AI, Full-Stack, Machine Learning, Data Engineering"},
            {"id": "cat_business", "name": "Business & Management", "department": "School of Business", "color": "#10B981", "description": "Global MBA, Supply Chain, International Trade, FinTech"},
            {"id": "cat_health", "name": "Healthcare & Nursing", "department": "School of Health Sciences", "color": "#EC4899", "description": "Hospital Administration, Nursing Adaptation, Clinical Research"},
            {"id": "cat_engineering", "name": "Engineering & Robotics", "department": "School of Engineering", "color": "#F59E0B", "description": "Automotive Engineering, Mechatronics, Renewable Energy"},
            {"id": "cat_language", "name": "Language & Test Prep", "department": "Language & Foundation", "color": "#8B5CF6", "description": "IELTS Academic, German A1-C1, French B2, TOEFL"},
            {"id": "cat_general", "name": "General Studies", "department": "Universal Foundation", "color": "#64748B", "description": "General Academic Curricula & Soft Skills"},
        ]
        for cat_data in categories:
            cat, created = CourseCategory.objects.get_or_create(id=cat_data["id"], defaults=cat_data)
            status_str = "Created" if created else "Exists"
            self.stdout.write(f"  - Category: {cat.name} ({status_str})")

        # 2. Global Tieup Policy
        policy, created = TieupPolicy.objects.get_or_create(
            id="global_policy",
            defaults={
                "min_commission_percent": 15.0,
                "target_commission_percent": 20.0,
                "partnership_criteria": "Accredited international universities with English-taught Bachelor/Master programs.",
                "student_requirements_guidelines": "Minimum 60% in Bachelor, IELTS 6.0 or Duolingo 110+.",
                "terms_expectations": "Direct student invoicing, 20% commission on first-year tuition upon visa grant.",
                "preferred_payment_terms": "Net 30 on student semester enrollment"
            }
        )
        self.stdout.write(f"  - Policy: {policy.id} ({'Created' if created else 'Exists'})")

        # 3. 17 AI Product Presets
        for prod_key, prompt_text in PROMPT_REGISTRY.items():
            display_name = prod_key.replace('_', ' ').title()
            preset, created = AIProductPreset.objects.get_or_create(
                id=prod_key,
                defaults={
                    "name": display_name,
                    "description": f"AI Engine configured for {display_name}",
                    "system_prompt": prompt_text,
                    "default_model": "gemini-2.5-flash",
                    "temperature": 0.7,
                    "tags": ["ila", prod_key],
                    "is_active": True
                }
            )
            self.stdout.write(f"  - AI Preset: {preset.name} ({'Created' if created else 'Exists'})")

        # 4. Sample University Tieup Leads
        sample_leads = [
            {
                "id": "lead_tum_01",
                "name": "Technical University of Munich (TUM)",
                "category": "Public University",
                "sub_category": "TU9 Excellence",
                "country": "Germany",
                "region": "Bavaria",
                "location_main": "Munich, Germany",
                "contact_person": "Dr. Hans Meyer",
                "contact_title": "Head of International Admissions",
                "contact_email": "international@tum.de",
                "website_url": "https://www.tum.de",
                "compatibility_score": 96,
                "commission_percent": 15.0,
                "min_ielts_score": 6.5,
                "german_level_required": "B2 (or English Track)",
                "tuition_fee_yearly": "€0 (Public)",
                "tuition_amount_eur": 0.0,
                "scholarship_available": True,
                "scholarship_details": "DAAD Merit Scholarships available.",
                "is_partner": True,
                "anti_spam_status": "verified"
            },
            {
                "id": "lead_bsbi_02",
                "name": "Berlin School of Business and Innovation (BSBI)",
                "category": "Private University",
                "sub_category": "Business & IT",
                "country": "Germany",
                "region": "Berlin",
                "location_main": "Berlin, Germany",
                "contact_person": "Elena Rossi",
                "contact_title": "Director of Global Partnerships",
                "contact_email": "partnerships@berlinsbi.com",
                "website_url": "https://www.berlinsbi.com",
                "compatibility_score": 92,
                "commission_percent": 25.0,
                "min_ielts_score": 6.0,
                "german_level_required": "None (English Only)",
                "tuition_fee_yearly": "€9,500/year",
                "tuition_amount_eur": 9500.0,
                "scholarship_available": True,
                "scholarship_details": "Up to 30% High Achiever Scholarship.",
                "is_partner": False,
                "anti_spam_status": "verified"
            }
        ]
        for lead_data in sample_leads:
            lead, created = TieupLead.objects.get_or_create(id=lead_data["id"], defaults=lead_data)
            self.stdout.write(f"  - Tieup Lead: {lead.name} ({'Created' if created else 'Exists'})")

        # 5. Sample Starter Course
        if not LibraryCourse.objects.exists():
            course = LibraryCourse.objects.create(
                id="course_germany_study_starter",
                title="Mastering Higher Education in Germany: Complete Blueprint",
                subtitle="From APS & Uni-Assist to Blocked Accounts and Visa Success",
                category="Study Abroad & Language Preparation",
                sub_category="Germany Pathways",
                delivery_path="online_cohort",
                overview="A comprehensive step-by-step masterclass curriculum designed for students targeting public and private German universities with 100% visa success rate.",
                total_chapters=3,
                tags=["Germany", "Visa", "Blocked Account", "APS", "Uni-Assist"],
                is_favorite=True,
                is_permanent=True,
                locked=True
            )
            CourseChapter.objects.create(
                id="chap_germany_1",
                course=course,
                chapter_number=1,
                title="APS Certification & Academic Evaluation Protocols",
                summary="Understanding the India APS verification timeline, document checklists, and submission strategy.",
                content="### Chapter 1: The APS Process Explained\n\nThe Academic Evaluation Centre (APS) certificate is a mandatory prerequisite for Indian students applying to German universities...",
                is_completed=True,
                sub_topics=["APS Document Checklist", "Notarization Requirements", "Verification Timelines"]
            )
            CourseChapter.objects.create(
                id="chap_germany_2",
                course=course,
                chapter_number=2,
                title="Uni-Assist Application & VPD Workflow",
                summary="Mastering the Uni-Assist portal, VPD conversions, and direct university portal submissions.",
                content="### Chapter 2: Uni-Assist Portal Deep-Dive\n\nUni-Assist acts as the central gatekeeper for over 180 German universities...",
                is_completed=False,
                sub_topics=["VPD Application", "ECTS Credit Matching", "Conditional Offers"]
            )
            CourseChapter.objects.create(
                id="chap_germany_3",
                course=course,
                chapter_number=3,
                title="Blocked Account Setup, Health Insurance & Visa Interview",
                summary="Financial readiness, statutory health insurance (TK/Barmer/AOK), and national student visa appointment strategy.",
                content="### Chapter 3: Visa Filing & Blocked Account Setup\n\nGerman law requires international students to demonstrate sufficient financial resources...",
                is_completed=False,
                sub_topics=["Coracle / Expatrio / Fintiba Comparison", "Statutory Health Insurance", "VFS Visa Interview Checklist"]
            )
            self.stdout.write(f"  - Starter Course: {course.title} (Created)")

        self.stdout.write(self.style.SUCCESS("SUCCESS: ILA AI Engine Hub seeded successfully!"))
