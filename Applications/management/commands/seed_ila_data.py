from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from Applications.Authentication.auth_models import FranchisePartner, AuditLog
from Applications.ILA_WEB.FrontOffice.frontoffice_models import Inquiry, FollowUpRecord
from Applications.ILA_WEB.Academics.academics_models import (
    GlobalCategory,
    GlobalSubCategory,
    TeachingStrategy,
    StudentAnalyzingStrategy,
    GlobalCourse,
    GlobalPath,
    GlobalBatch,
    ClassScheduleSession,
)
from Applications.ILA_WEB.HRMS.hrms_models import StaffProfile, HRCandidate, EnterpriseTask, ApprovalRequest
from Applications.ILA_WEB.Finance.finance_models import FinancialLedger, SalesRecord, FundPool, CommissionItem
from Applications.ILA_WEB.Rewards.rewards_models import ReferralRecord, TierRule

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial enterprise data for ILA Global (Categories, Courses, Strategies, Staff, Inquiries, Ledger)"

    def handle(self, *args, **options):
        self.stdout.write("Starting ILA Global Enterprise data seeding...")

        # 1. Super Admin User
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@ilaglobal.de",
                "fullname": "ILA Executive Super Admin",
                "role": "Super Admin",
                "department": "Super Admin",
                "is_admin": True,
                "is_staff": True,
                "is_superuser": True,
                "is_email_verified": True,
            }
        )
        if created:
            admin_user.set_password("Admin@123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created default Super Admin user (admin / Admin@123)"))

        # 2. Staff Users & Profiles
        staff_data = [
            ("klaus.mueller", "klaus@ilaglobal.de", "Klaus Mueller", "Academic Director", "Academic", "STAFF-001", Decimal("4500.00")),
            ("priya.sundaram", "priya@ilaglobal.de", "Priya Sundaram", "Head of Admissions", "Study Abroad", "STAFF-002", Decimal("3800.00")),
            ("meera.kapoor", "meera@ilaglobal.de", "Meera Kapoor", "Front Office Lead Counselor", "Front Office", "STAFF-003", Decimal("3200.00")),
            ("stefan.weber", "stefan@ilaglobal.de", "Stefan Weber", "Visa & Legal Compliance Officer", "Visa", "STAFF-004", Decimal("4000.00")),
        ]

        staff_users = {}
        for username, email, fullname, role, dept, emp_id, salary in staff_data:
            user, u_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "fullname": fullname,
                    "role": "Academic Counselor" if "Counselor" in role else "HR Manager",
                    "department": dept,
                    "is_staff": True,
                    "is_email_verified": True,
                }
            )
            if u_created:
                user.set_password("Staff@123")
                user.save()

            profile, _ = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": emp_id,
                    "department": dept,
                    "monthly_salary": salary,
                    "status": "Active",
                }
            )
            staff_users[username] = user

        self.stdout.write(self.style.SUCCESS("Seeded Staff profiles"))

        # 3. Global Categories & Subcategories
        categories = [
            ("cat-1", "Education & Languages", "EDU-LANG", "German CEFR A1-C2, IELTS, TOEFL, Professional Language Programs"),
            ("cat-2", "Study Abroad & Universities", "STUDY-EU", "European & German university admissions, APS, and bachelor/master pathways"),
            ("cat-3", "Visa & Immigration Compliance", "VISA-IMM", "Chancenkarte Opportunity Card, Student Visa, Blocked Account (€11,900)"),
            ("cat-4", "Work While You Study (Ausbildung)", "AUSB-DUAL", "Dual-vocational apprenticeships with €1,200/mo corporate stipends"),
            ("cat-5", "Software & Cloud Engineering", "TECH-SW", "Full-Stack Development, Python, DevOps, and Enterprise Cloud"),
            ("cat-6", "SAP S/4HANA Enterprise", "ERP-SAP", "SAP FI/CO, MM, SD, and ABAP technical consultant certifications"),
        ]

        for cat_id, name, code, desc in categories:
            cat, _ = GlobalCategory.objects.get_or_create(
                id=cat_id,
                defaults={"name": name, "code": code, "description": desc}
            )
            GlobalSubCategory.objects.get_or_create(
                category=cat,
                name=f"{name} Foundation",
                defaults={"code": f"{code}-FOUND"}
            )

        self.stdout.write(self.style.SUCCESS("Seeded Global Categories & Subcategories"))

        # 4. Teaching & Student Analyzing Strategies
        teaching_strategies = [
            ("ts-1", "CEFR Immersive Sprint", "German Language", "High-frequency communicative fluency", "Active roleplays, listening drills, cultural idioms", "Sprint (8 weeks)", "Beginners A1-B1"),
            ("ts-2", "Dual-Vocational Apprenticeship Pacing", "Ausbildung", "B1 German + Hospital/Hotel workplace terms", "Bilingual glossaries, patient case simulations", "Structured (12 weeks)", "Ausbildung applicants"),
            ("ts-3", "Technical & Medical FSP Simulation", "Healthcare", "Specialist German medical documentation & doctor-patient dialogue", "Case study audits, mock medical boards", "Intensive (16 weeks)", "Doctors & Nurses"),
            ("ts-4", "Opportunity Card Rapid Score Builder", "Chancenkarte", "Points maximization for German Job Search Visa", "Document scoring, Europass CV localization, interview prep", "Fast-track (4 weeks)", "Skilled workers & graduates"),
        ]

        for ts_id, name, cat, tagline, desc, pacing, target in teaching_strategies:
            TeachingStrategy.objects.get_or_create(
                id=ts_id,
                defaults={
                    "name": name,
                    "category": cat,
                    "tagline": tagline,
                    "description": desc,
                    "pacing_model": pacing,
                    "target_learner": target,
                    "default_active": True,
                }
            )

        analyzing_strategies = [
            ("sas-1", "Vocabulary Retention Decay Index", "Retention Rate", "65%", "Analyzes spaced repetition quiz accuracy; schedules adaptive flashcard sprints.", "Auto-schedule review drill"),
            ("sas-2", "German Grammar Inversion Accuracy", "Grammar Precision", "75%", "Monitors word order and dative/accusative prepositions in essays.", "Assign targeted grammar workbook"),
            ("sas-3", "Visa Readiness & Profile Score", "Audit Score", "80%", "Verifies APS, blocked account, and B2 certificate completion before embassy booking.", "Unlock embassy queue ticket"),
        ]

        for sas_id, name, metric, threshold, desc, action in analyzing_strategies:
            StudentAnalyzingStrategy.objects.get_or_create(
                id=sas_id,
                defaults={
                    "name": name,
                    "target_metric": metric,
                    "threshold": threshold,
                    "description": desc,
                    "adaptation_action": action,
                    "active": True,
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded Pedagogic Strategies"))

        # 5. Global Courses, Paths & Batches
        edu_cat = GlobalCategory.objects.get(id="cat-1")
        visa_cat = GlobalCategory.objects.get(id="cat-3")
        ausb_cat = GlobalCategory.objects.get(id="cat-4")

        courses = [
            ("1", "German Language CEFR A1–B2 Complete Masterclass", "Language Proficiency", "Goethe / Telc Accredited", edu_cat, Decimal("850.00"), 48, "6 Months"),
            ("2", "German Opportunity Card (Chancenkarte) Accelerator", "Immigration & Career", "Full Document & Job Placement Support", visa_cat, Decimal("1200.00"), 24, "3 Months"),
            ("3", "Ausbildung Nursing & Healthcare Dual-Apprenticeship", "Vocational & Stipend", "Paid €1,200/mo corporate stipend in Germany", ausb_cat, Decimal("1500.00"), 36, "4 Months"),
        ]

        for c_id, name, top_title, subtitle, cat, fee, chapters, duration in courses:
            course, _ = GlobalCourse.objects.get_or_create(
                id=c_id,
                defaults={
                    "name": name,
                    "top_title": top_title,
                    "subtitle": subtitle,
                    "category": cat,
                    "fee": fee,
                    "chapters_count": chapters,
                    "duration": duration,
                    "enrolled_count": 42,
                    "course_structure": "Module 1: Orientation & Foundations\nModule 2: Core Fluency\nModule 3: Certification Exam Mastery",
                }
            )

            # Add Path
            path, _ = GlobalPath.objects.get_or_create(
                id=f"p-{c_id}-1",
                defaults={
                    "course": course,
                    "name": "Intensive Morning Fast-Track",
                    "code": f"P-{c_id}-AM",
                    "methods": "Live Interactive Video + Daily Whiteboard",
                    "position": 1,
                    "starting_date": timezone.now().date(),
                    "ending_date": timezone.now().date() + timedelta(days=90),
                }
            )

            # Add Batch
            GlobalBatch.objects.get_or_create(
                id=f"b-{c_id}-1",
                defaults={
                    "course": course,
                    "path": path,
                    "name": "Munich Morning Cohort 2026",
                    "code": f"BAT-{c_id}-MUC",
                    "timings": ["09:00 - 11:30 CET", "14:00 - 16:30 CET"],
                    "starting_date": timezone.now().date() + timedelta(days=7),
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded Courses, Paths & Batches"))

        # 6. Front-Office CRM Inquiries
        inquiries = [
            ("inq-101", "ILA-WALK-101", "Walk-in", "Ananya Sharma", "ananya.s@gmail.com", "+91 9845012345", "Education", "German Language CEFR A1–B2 Complete Masterclass", Decimal("850.00"), Decimal("850.00"), "Paid", "Closed Won", "Completed", "Front-Desk Reception", "Due Today"),
            ("inq-102", "ILA-WALK-102", "Walk-in", "Rahul Varma", "rahul.v@outlook.com", "+91 9876543210", "Visa", "German Opportunity Card (Chancenkarte) Accelerator", Decimal("1200.00"), Decimal("600.00"), "Partially Paid", "In Progress", "Documentation", "Walk-in Desk", "Scheduled"),
            ("inq-103", "ILA-ONL-103", "Online", "Kavita Patel", "kavita.p@gmail.com", "+91 9123456780", "Work While You Study", "Ausbildung Nursing & Healthcare Dual-Apprenticeship", Decimal("1500.00"), Decimal("0.00"), "Pending", "New Lead", "Assessment", "Website Hero Portal", "Pending"),
        ]

        for i_id, token, lead_type, name, email, phone, cat, course_name, total, paid, pay_status, crm_status, pipe_stage, src, f_status in inquiries:
            inq, _ = Inquiry.objects.get_or_create(
                id=i_id,
                defaults={
                    "token_number": token,
                    "lead_type": lead_type,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "category": cat,
                    "course_name": course_name,
                    "total_amount": total,
                    "amount_paid": paid,
                    "payment_status": pay_status,
                    "crm_status": crm_status,
                    "pipeline_stage": pipe_stage,
                    "source": src,
                    "follow_up_status": f_status,
                    "assigned_staff": staff_users.get("meera.kapoor"),
                    "follow_up_date": timezone.now().date(),
                }
            )

            # Follow up record
            FollowUpRecord.objects.get_or_create(
                id=f"fl-{i_id}",
                defaults={
                    "inquiry": inq,
                    "staff": staff_users.get("meera.kapoor"),
                    "channel": "In-Person" if lead_type == "Walk-in" else "Phone Call",
                    "notes": f"Initial consultation completed. Candidate demonstrated strong interest in {course_name}.",
                    "outcome": "Interested - Callback",
                    "next_follow_up_date": timezone.now().date() + timedelta(days=3),
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded CRM Inquiries & Follow-up History"))

        # 7. Financial Ledger & Funds
        ledger_entries = [
            ("REV-101", "income", "Education Revenue", "Tuition Fee Enrollment: Ananya Sharma (German A1-B2)", Decimal("850.00"), "ILA-WALK-101"),
            ("REV-102", "income", "Visa Services", "First Installment Chancenkarte: Rahul Varma", Decimal("600.00"), "ILA-WALK-102"),
            ("EXP-101", "expense", "Marketing & Lead Gen", "Google Search Ads Frankfurt & Bangalore campaigns", Decimal("450.00"), "MKT-2026-03"),
            ("EXP-102", "expense", "Operations & Software", "AWS Frankfurt Cloud Hosting & Zoom Enterprise licenses", Decimal("320.00"), "OPS-2026-03"),
        ]

        for l_id, t_type, cat, desc, amount, ref in ledger_entries:
            FinancialLedger.objects.get_or_create(
                id=l_id,
                defaults={
                    "transaction_type": t_type,
                    "category": cat,
                    "description": desc,
                    "amount": amount,
                    "reference_id": ref,
                    "created_by": admin_user,
                }
            )

        # Fund Pools
        fund_pools = [
            ("FUND-OPS", "Core Operations Pool", "Operations", Decimal("50000.00"), Decimal("14200.00")),
            ("FUND-MKT", "Global Marketing Studio", "Marketing", Decimal("25000.00"), Decimal("8500.00")),
            ("FUND-RES", "Statutory Reserve Fund", "Reserve", Decimal("100000.00"), Decimal("0.00")),
        ]
        for f_id, name, cat, allocated, utilized in fund_pools:
            FundPool.objects.get_or_create(
                id=f_id,
                defaults={
                    "fund_name": name,
                    "category": cat,
                    "allocated_amount": allocated,
                    "utilized_amount": utilized,
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded Financial Ledger & Fund Pools"))

        # 8. Tier Rules & Rewards
        tiers = [
            ("TIER-BRONZE", "Bronze", 0, Decimal("1.00"), Decimal("50.00"), "#CD7F32"),
            ("TIER-SILVER", "Silver", 5, Decimal("1.25"), Decimal("75.00"), "#C0C0C0"),
            ("TIER-GOLD", "Gold", 15, Decimal("1.50"), Decimal("120.00"), "#FFD700"),
            ("TIER-PLATINUM", "Platinum", 30, Decimal("2.00"), Decimal("200.00"), "#E5E4E2"),
        ]
        for t_id, name, min_r, mult, base, color in tiers:
            TierRule.objects.get_or_create(
                id=t_id,
                defaults={
                    "tier_name": name,
                    "min_referrals": min_r,
                    "bonus_multiplier": mult,
                    "base_reward": base,
                    "color": color,
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded Tier Rules for Rewards"))

        # 9. Audit Log Entry
        AuditLog.objects.get_or_create(
            id="UPD-INIT",
            defaults={
                "user": admin_user,
                "department": "Super Admin",
                "category": "System",
                "action": "Enterprise Database Seeding Initialized",
                "details": "Automated provisioning of ILA Global 2_ILA_WEB_v3.3 DRF platform schema and seed records.",
            }
        )

        self.stdout.write(self.style.SUCCESS("ILA Global Enterprise data seeding completed successfully!"))
