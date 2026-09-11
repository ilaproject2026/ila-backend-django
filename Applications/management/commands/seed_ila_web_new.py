from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import uuid

from Applications.ILA_WEB_NEW.study_abroad.models import (
    Country,
    College,
    StudyAbroadCourse,
    DocumentChecklist,
    ConsultantATSTask,
    CountryTieUpCategory,
    StudentApplication,
)
from Applications.ILA_WEB_NEW.work_study.models import (
    WorkStudyPackage,
    WorkStudyRoleFeature,
    WorkStudyStream,
    WorkStudyCandidate,
)
from Applications.ILA_WEB_NEW.job_search.models import (
    PartnerCompany,
    JobListing,
    CandidateResume,
    JobMatch,
)
from Applications.ILA_WEB_NEW.rewards_plan.models import (
    RewardPlan,
    RewardRule,
    RewardCatalogItem,
    RewardRedemption,
)
from Applications.ILA_WEB_NEW.communication_engine.models import (
    CommunicationWorkflowRule,
    DispatchLog,
)
from Applications.ILA_WEB_NEW.intake_tracking.models import (
    DepartmentInquiry,
    FollowUpAutoTriggerRule,
    SocialMediaCampaign,
)


class Command(BaseCommand):
    help = "Seeds initial production setup and demo dataset for ILA_WEB_NEW ecosystem"

    def handle(self, *args, **options):
        self.stdout.write("==================================================")
        self.stdout.write("Starting ILA_WEB_NEW Ecosystem Setup & Data Seed...")
        self.stdout.write("==================================================")

        # ----------------------------------------------------------------------
        # 1. STUDY ABROAD: Countries, Colleges, Categories & Courses
        # ----------------------------------------------------------------------
        countries_data = [
            ("Germany", "DE", "🇩🇪", "National Student Visa (APS / §16b)", "EUR (€)", "€0 - €1,500 / yr", "€934 / mo (Blocked Account)", "World-renowned public university system with €0 tuition and post-study EU Blue Card pathways."),
            ("United Kingdom", "GB", "🇬🇧", "Student Visa (Subclass 500 / Tier 4)", "GBP (£)", "£14,000 - £26,000 / yr", "£1,023 / mo", "Premier global education hub with 1-Year Masters and 2-Year Graduate Route Post-Study Work Permit."),
            ("Canada", "CA", "🇨🇦", "Study Permit (SDS / Non-SDS)", "CAD ($)", "CAD 16,000 - 28,000 / yr", "CAD 1,720 / mo (GIC)", "3-Year Post-Graduation Work Permit (PGWP) and expedited Express Entry PR corridors."),
            ("Australia", "AU", "🇦🇺", "Higher Education Visa (Subclass 500)", "AUD ($)", "AUD 22,000 - 38,000 / yr", "AUD 2,050 / mo", "Group of Eight (Go8) research excellence and 2-4 year Temporary Graduate Work Visas (Subclass 485)."),
            ("France", "FR", "🇫🇷", "VLS-TS Student Long-Stay Visa", "EUR (€)", "€2,770 - €3,770 / yr", "€800 / mo", "Subsidized public education, Grandes Écoles management prestige, and 2-Year post-study APS visa."),
            ("Ireland", "IE", "🇮🇪", "Stamp 2 Student Permission", "EUR (€)", "€10,000 - €22,000 / yr", "€850 / mo", "European tech and pharmaceutical headquarters hub with 2-Year Third Level Graduate Scheme."),
        ]

        created_countries = {}
        for name, code, flag, visa_type, cur, tuition, living, desc in countries_data:
            country, _ = Country.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "flag": flag,
                    "visa_type": visa_type,
                    "currency": cur,
                    "avg_tuition": tuition,
                    "living_cost": living,
                    "description": desc,
                    "status": "Active",
                }
            )
            created_countries[code] = country

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(created_countries)} Study Abroad Countries"))

        # Country Tie-Up Navigation Categories
        categories_map = {
            "DE": [
                ("all", "All Programs", "All", 0),
                ("public_uni", "Public University (€0 Tuition)", "€0 Tuition", 1),
                ("masters", "Masters (M.Sc / M.Eng)", "2 Years", 2),
                ("bachelors", "Bachelors (B.Sc / B.Eng)", "3-4 Years", 3),
                ("ausbildung", "Ausbildung (Paid Dual Study)", "Stipend €1,100/mo", 4),
            ],
            "GB": [
                ("all", "All Programs", "All", 0),
                ("russell_group", "Russell Group (Top 100 QS)", "Prestigious", 1),
                ("masters", "Masters (1-Year Fast Track)", "1 Year", 2),
                ("bachelors", "Bachelors (Honours)", "3 Years", 3),
            ],
            "CA": [
                ("all", "All Programs", "All", 0),
                ("public_uni", "Public College / University", "PGWP Eligible", 1),
                ("coop_degree", "Co-Op Degree Programs", "Paid Co-Op", 2),
                ("masters", "Masters (Postgraduate)", "2 Years", 3),
            ],
        }

        for ccode, cats in categories_map.items():
            ct = created_countries.get(ccode)
            if ct:
                for cat_id, label, badge, order in cats:
                    CountryTieUpCategory.objects.get_or_create(
                        country=ct,
                        category_id=cat_id,
                        defaults={
                            "label": label,
                            "badge": badge,
                            "display_order": order,
                            "is_active": True,
                        }
                    )

        # Colleges
        colleges_data = [
            ("DE", "Technical University of Munich (TUM)", "Munich", "TU9 / QS #28", "Technical University", "Min 7.5 CGPA, APS Certificate, IELTS 6.5 or B2 German"),
            ("DE", "RWTH Aachen University", "Aachen", "TU9 / QS #99", "Technical University", "Min 7.0 CGPA, APS Certificate, GRE Recommended for CS"),
            ("DE", "Heidelberg University", "Heidelberg", "Excellence / QS #84", "Public", "Min 7.2 CGPA, APS, B2 German for Medical/Life Sciences"),
            ("DE", "Berlin International University of Applied Sciences", "Berlin", "State-Recognized UAS", "University of Applied Sciences", "Min 6.5 CGPA, IELTS 6.0, Direct English Track"),
            ("DE", "Klinikum Stuttgart Health Academy", "Stuttgart", "Premier Healthcare Facility", "Public", "B2 German (Goethe/TELC), 12th Standard Science (PCB)"),
            ("GB", "Imperial College London", "London", "Russell Group / QS #2", "Public", "First Class Honours (8.0+ CGPA), IELTS 7.0"),
            ("GB", "University of Manchester", "Manchester", "Russell Group / QS #34", "Public", "Min 7.2 CGPA, IELTS 6.5"),
            ("CA", "University of Toronto", "Toronto", "U15 / QS #21", "Public", "Min 7.8 CGPA, IELTS 7.0, WES Evaluation"),
            ("AU", "University of Melbourne", "Melbourne", "Go8 / QS #13", "Public", "Min 7.5 CGPA, IELTS 6.5"),
            ("IE", "Trinity College Dublin", "Dublin", "QS #87", "Public", "Min 7.0 CGPA, IELTS 6.5"),
        ]

        created_colleges = {}
        for ccode, name, city, rank, itype, crit in colleges_data:
            country = created_countries.get(ccode)
            if country:
                col, _ = College.objects.get_or_create(
                    country=country,
                    name=name,
                    defaults={
                        "city": city,
                        "ranking": rank,
                        "institution_type": itype,
                        "admission_criteria": crit,
                        "status": "Partnered",
                    }
                )
                created_colleges[name] = col

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(created_colleges)} Partner Colleges"))

        # Study Abroad Courses
        courses_data = [
            ("DE", "Technical University of Munich (TUM)", "M.Sc. Data Engineering and Analytics", "Masters", "2 Years (4 Semesters)", "English", "€0 (Semester fee ~€150)", 7.8, 6.5, "None", ["Winter (Oct)", "Summer (Apr)"]),
            ("DE", "RWTH Aachen University", "M.Sc. Automotive Engineering & Sustainable Mobility", "Masters", "2 Years (4 Semesters)", "English", "€0 (Semester fee ~€300)", 7.5, 6.5, "None", ["Winter (Oct)"]),
            ("DE", "Berlin International University of Applied Sciences", "B.A. International Management & Tech", "Bachelors", "3 Years (6 Semesters)", "English", "€7,920 / yr", 6.5, 6.0, "None", ["Winter (Oct)", "Summer (Apr)"]),
            ("DE", "Klinikum Stuttgart Health Academy", "Dual-Vocational Healthcare & Nursing (Pflegefachmann/-frau)", "Ausbildung", "3 Years (Paid Dual Study)", "German", "€0 (Stipend: €1,250 - €1,400 / mo)", 6.0, 0.0, "B2", ["Winter (Oct)", "Spring (Mar)"]),
            ("GB", "Imperial College London", "M.Sc. Computing (Artificial Intelligence and Machine Learning)", "Masters", "1 Year (Fast Track)", "English", "£38,500 / yr", 8.2, 7.0, "None", ["Autumn (Sep)"]),
            ("IE", "Trinity College Dublin", "M.Sc. High Performance Computing & Cloud Architecture", "Masters", "1 Year (Full Time)", "English", "€24,500 / yr", 7.0, 6.5, "None", ["Autumn (Sep)"]),
        ]

        for ccode, col_name, cname, deg, dur, lang, tuition, cgpa, ielts, germ, intakes in courses_data:
            country = created_countries.get(ccode)
            college = created_colleges.get(col_name)
            if country and college:
                StudyAbroadCourse.objects.get_or_create(
                    country=country,
                    college=college,
                    course_name=cname,
                    defaults={
                        "degree": deg,
                        "duration": dur,
                        "language": lang,
                        "tuition_per_year": tuition,
                        "min_cgpa": cgpa,
                        "min_ielts": ielts,
                        "min_german_level": germ,
                        "intake_season": intakes,
                        "is_featured": True,
                    }
                )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Study Abroad Courses"))

        # Document Checklists
        checklists = [
            ("Germany", "All", "Valid International Passport", True, "PDF", 5, "Must have at least 12 months validity remaining from intended departure date."),
            ("Germany", "Masters", "APS Certificate (Akademische Prüfstelle)", True, "PDF", 10, "Mandatory verification certificate issued by the German Embassy New Delhi."),
            ("Germany", "All", "Official Degree Transcripts & Consolidated Marksheet", True, "PDF", 10, "Attested university degree transcripts from recognized AICTE/UGC universities."),
            ("Germany", "All", "Proof of English Proficiency (IELTS Academic / TOEFL)", True, "PDF", 5, "Minimum score of 6.5 overall for Masters, or IELTS 6.0 for Bachelors."),
            ("Germany", "Ausbildung", "Goethe / TELC German B2 Language Certificate", True, "PDF", 5, "Official CEFR B2 certificate mandatory for healthcare and technical apprenticeships."),
            ("Germany", "All", "Blocked Account Confirmation (€11,904)", True, "PDF", 5, "Official Sperrkonto opening statement from Expatrio, Coracle, or Fintiba."),
            ("Germany", "All", "Statement of Purpose (SOP) & Europass Resume", True, "PDF", 5, "1-2 page academic motivation letter detailing research and career pathway."),
        ]

        for ctry, track, doc, req, fmt, maxs, dsc in checklists:
            DocumentChecklist.objects.get_or_create(
                country=ctry,
                doc_name=doc,
                defaults={
                    "course_track": track,
                    "is_required": req,
                    "accepted_formats": fmt,
                    "max_size_mb": maxs,
                    "description": dsc,
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Document Checklists"))

        # ATS Tasks
        ats_tasks = [
            ("Kavita Iyer", "kavita.iyer@example.com", "+91 98450 11223", "Germany", "M.Sc. Data Engineering and Analytics", 94, "Document Verification", "Sarah Müller (Senior Admissions Lead)"),
            ("Aakash Nair", "aakash.nair@example.com", "+91 97451 99887", "Germany", "Dual-Vocational Healthcare & Nursing", 91, "Interview Scheduled", "Hans Weber (German Project Lead)"),
            ("Rohan Desai", "rohan.desai@example.com", "+91 98200 44332", "United Kingdom", "M.Sc. Computing (AI and ML)", 88, "University Review", "David Smith (UK Admissions Desk)"),
            ("Meghna Pillai", "meghna.pillai@example.com", "+91 94471 22334", "Germany", "M.Sc. Automotive Engineering", 95, "Visa Preparation", "Sarah Müller (Senior Admissions Lead)"),
        ]

        for sname, semail, sphone, ctry, crs, score, stage, cons in ats_tasks:
            task, created = ConsultantATSTask.objects.get_or_create(
                student_email=semail,
                defaults={
                    "student_account_id": f"STU-{uuid.uuid4().hex[:6].upper()}",
                    "student_name": sname,
                    "student_phone": sphone,
                    "target_country": ctry,
                    "target_course": crs,
                    "match_score": score,
                    "stage": stage,
                    "assigned_consultant": cons,
                    "uploaded_documents": [
                        {"docName": "Valid International Passport", "fileName": "passport_scan.pdf", "verified": True},
                        {"docName": "APS Certificate", "fileName": "aps_verification.pdf", "verified": stage != "Lead / Intake"},
                        {"docName": "Degree Transcripts", "fileName": "transcripts_consolidated.pdf", "verified": True},
                    ],
                    "consultant_notes": [
                        {"author": cons, "note": "Initial documents audited. Candidate profile meets all eligibility requirements.", "timestamp": str(timezone.now())}
                    ]
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Consultant ATS Pipeline Tasks"))

        # ----------------------------------------------------------------------
        # 2. WORK & STUDY HUB: Packages, Streams & Candidates
        # ----------------------------------------------------------------------
        wsp_data = [
            (
                "WSP-IND-01",
                "work-in-india",
                "Work & Study in India",
                "Office Administration, Accounts & Corporate Billing",
                "Operations",
                "₹18,000 - ₹25,000 / mo",
                "6 Months Initial Intensive Training",
                "6 Months Corporate Hands-On Pilot",
                "1-Year Verified Corporate Certificate & Permanent Placement Option",
                "Corporate office administration, ERP data entry, financial ledger maintenance, and GST billing for Indian and multinational clients.",
                ["Office Accounting & Tally Prime", "Client Interaction & Escalations", "Corporate Documentation & MIS Reports"],
                ["Finance & Corporate Accounts", "Operations Management", "Customer Relations & CRM"]
            ),
            (
                "WSP-IND-02",
                "work-in-india",
                "Work & Study in India",
                "Junior Full-Stack Web Development & Cloud Operations",
                "Tech & AI",
                "₹20,000 - ₹30,000 / mo",
                "6 Months Live Project Lab",
                "6 Months Client Deployment",
                "Full-Stack Certification + AWS Cloud Practitioner Voucher",
                "Frontend React/TypeScript development, RESTful Django backend engineering, and Docker containerized cloud deployments.",
                ["Modern React & TypeScript UI", "Django REST Framework APIs", "CI/CD & Docker Cloud Pipelines"],
                ["Full-Stack Engineering", "Frontend Architecture", "DevOps & Cloud"]
            ),
            (
                "WSP-GER-01",
                "german-projects",
                "German Onboarding Projects",
                "Healthcare Assistant & Nursing Dual Apprenticeship",
                "Healthcare",
                "€1,250 - €1,500 / mo",
                "8 Months B2 German & Medical Terminology (India)",
                "3 Years Dual Clinical Training (Germany)",
                "German State Registered Nurse (Pflegefachmann/Pflegefachfrau)",
                "100% tuition-free dual-training with Germany's top hospital groups. Receive monthly stipends, health insurance, and permanent residence pathway.",
                ["Intensive B1/B2 German Certification", "Clinical Anatomy & Patient Care Practice", "Direct Hospital Contract Signing"],
                ["General Nursing", "Elderly & Geriatric Care", "Pediatric Nursing"]
            ),
            (
                "WSP-GER-02",
                "german-projects",
                "German Onboarding Projects",
                "Industrial Mechatronics & Robotics Dual-Study",
                "Engineering",
                "€1,150 - €1,350 / mo",
                "6 Months German & Technical Foundations",
                "3.5 Years Corporate Apprenticeship (Baden-Württemberg)",
                "IHK Certified Industrial Mechatronics Technician",
                "Hands-on dual apprenticeship with leading German automotive and manufacturing enterprises in robotics, PLC programming, and precision automation.",
                ["B1/B2 Technical German Sprint", "PLC Programming & Circuit Diagnostics", "German Industrial Safety Standards"],
                ["Industrial Mechatronics", "Automotive Systems", "CNC & Precision Tooling"]
            ),
            (
                "WSP-ABR-01",
                "work-in-abroad",
                "Work & Study in Abroad",
                "European Supply Chain & Logistics Operations",
                "Logistics",
                "€1,100 - €1,400 / mo",
                "4 Months Foundation & Warehouse Management Systems",
                "1-2 Years Post-Arrival Part-Time Student Work",
                "EU Logistics Safety & Operations Certificate",
                "Master global supply chain workflows, port handling documentation, and warehouse automation while enrolled in accredited European universities.",
                ["WMS & RFID Inventory Control", "Customs & Freight Clearance Documents", "Safe Operating Procedures in EU Warehousing"],
                ["Supply Chain Management", "Port & Air Freight Logistics", "Inventory Analytics"]
            ),
            (
                "WSP-REW-01",
                "reward-study-platform",
                "Reward & Study Platform",
                "Global Junior Educational Consultant & Campus Lead",
                "Consultancy",
                "₹15,000 + Milestone Bonuses",
                "4 Weeks Fast-Track Consultant Training",
                "Continuous Ambassador Network Engagement",
                "ILA Junior Consultant Certificate & Revenue Share Royalty",
                "Guide fellow students toward study abroad and German pathway programs. Earn monthly cash incentives and unlock fully paid European exposure trips.",
                ["Global University System Mastery", "Counseling & Visa Screening Skills", "Affiliate Dashboard & Lead Management"],
                ["Study Abroad Counseling", "Language Course Ambassadorship", "Corporate Institutional Tie-Ups"]
            ),
        ]

        for pid, cat, cat_lbl, title, badge, stipend, t_dur, i_dur, cert, desc, roles, streams in wsp_data:
            pkg, _ = WorkStudyPackage.objects.get_or_create(
                id=pid,
                defaults={
                    "category": cat,
                    "category_label": cat_lbl,
                    "title": title,
                    "badge": badge,
                    "stipend": stipend,
                    "training_duration": t_dur,
                    "internship_duration": i_dur,
                    "certification": cert,
                    "action_text": "Apply Now",
                    "description": desc,
                    "status": "Active",
                }
            )

            # Features / Roles
            for idx, r in enumerate(roles):
                WorkStudyRoleFeature.objects.get_or_create(
                    package=pkg,
                    title=r,
                    defaults={"order": idx, "is_milestone": idx < 3}
                )

            # Streams
            for s in streams:
                WorkStudyStream.objects.get_or_create(
                    package=pkg,
                    name=s,
                    defaults={"code": s.upper().replace(" ", "_")}
                )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Work & Study Packages, Roles and Streams"))

        # Candidates
        candidates_data = [
            ("Varun Sen", "varun.sen@example.com", "+91 98112 33445", "WSP-IND-02", "Full-Stack Engineering", "AI & Skill Training", "Active", "₹20,000 / mo", 45),
            ("Divya Nair", "divya.nair@example.com", "+91 97450 77665", "WSP-GER-01", "General Nursing", "German Sponsor Match", "Active", "€1,250 / mo", 85),
            ("Siddharth Rao", "siddharth.rao@example.com", "+91 98451 44556", "WSP-GER-02", "Industrial Mechatronics", "Active Internship / Pilot", "Active", "€1,150 / mo", 65),
            ("Aishwarya Menon", "aishwarya.menon@example.com", "+91 99955 12345", "WSP-REW-01", "Study Abroad Counseling", "Graduated & Relocated", "Paid", "₹18,500 / mo", 100),
        ]

        for cname, cemail, cphone, pkg_id, stream, stage, s_stat, cur_stipend, prog in candidates_data:
            pkg = WorkStudyPackage.objects.filter(id=pkg_id).first()
            WorkStudyCandidate.objects.get_or_create(
                email=cemail,
                defaults={
                    "name": cname,
                    "phone": cphone,
                    "package": pkg,
                    "selected_stream": stream,
                    "stage": stage,
                    "stipend_status": s_stat,
                    "current_stipend": cur_stipend,
                    "progress_pct": prog,
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Work & Study Candidates"))

        # ----------------------------------------------------------------------
        # 3. JOB SEARCH & TALENT MATCHING
        # ----------------------------------------------------------------------
        companies_data = [
            ("BMW Group", "🚗", "Automotive & Mobility", "Munich, Germany", "Germany", "Strategic Partner", "https://bmwgroup.jobs"),
            ("Siemens AG", "⚡", "Industrial Automation & Software", "Erlangen / Berlin, Germany", "Germany", "Strategic Partner", "https://jobs.siemens.com"),
            ("SAP SE", "💻", "Enterprise Cloud Software", "Walldorf, Germany", "Germany", "Strategic Partner", "https://jobs.sap.com"),
            ("Robert Bosch GmbH", "🔧", "Automotive & IoT Engineering", "Stuttgart, Germany", "Germany", "Enterprise Client", "https://bosch.com/careers"),
            ("Klinikum Stuttgart Healthcare Group", "🏥", "Hospital & Medical Care", "Stuttgart, Germany", "Germany", "Direct Recruiter", "https://klinikum-stuttgart.de/karriere"),
        ]

        created_companies = {}
        for cname, logo, ind, loc, ctry, tier, web in companies_data:
            comp, _ = PartnerCompany.objects.get_or_create(
                name=cname,
                defaults={
                    "logo": logo,
                    "industry": ind,
                    "location": loc,
                    "country": ctry,
                    "hiring_tier": tier,
                    "website": web,
                    "status": "Active",
                }
            )
            created_companies[cname] = comp

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(created_companies)} Partner Companies"))

        jobs_data = [
            ("SAP SE", "Cloud Infrastructure & Kubernetes DevOps Engineer", "Software & IT", "Germany", "Walldorf", "€75,000 - €92,000 / yr", "Full-Time Permanent", True, ["Kubernetes", "Docker", "Go", "AWS", "Terraform"], "3+ Years", "None", 4),
            ("BMW Group", "Autonomous Driving Perception Software Engineer", "Engineering", "Germany", "Munich", "€78,000 - €95,000 / yr", "Full-Time Permanent", True, ["C++", "ROS2", "Computer Vision", "Python", "Linux"], "2+ Years", "A2", 3),
            ("Siemens AG", "Industrial Automation & PLC Systems Engineer", "Engineering", "Germany", "Erlangen", "€65,000 - €80,000 / yr", "Full-Time Permanent", True, ["PLC Siemens S7", "TIA Portal", "SCADA", "Industrial Ethernet"], "2+ Years", "B1", 2),
            ("Klinikum Stuttgart Healthcare Group", "Certified Registered Nurse (Gesundheits- und Krankenpfleger)", "Healthcare", "Germany", "Stuttgart", "€42,000 - €54,000 / yr", "Full-Time Permanent", True, ["B.Sc Nursing", "Patient Care", "ICU Support", "Medical Documentation"], "1+ Years", "B2", 15),
            ("Robert Bosch GmbH", "Embedded Firmware Engineer (AUTOSAR / C)", "Software & IT", "Germany", "Stuttgart", "€72,000 - €88,000 / yr", "Full-Time Permanent", True, ["C", "AUTOSAR", "CAN / LIN Bus", "Microcontrollers"], "3+ Years", "None", 5),
        ]

        for comp_name, jtitle, domain, ctry, city, sal, ctype, blue_card, skills, exp, g_lvl, openings in jobs_data:
            comp = created_companies.get(comp_name)
            if comp:
                JobListing.objects.get_or_create(
                    company=comp,
                    title=jtitle,
                    defaults={
                        "domain": domain,
                        "country": ctry,
                        "city": city,
                        "salary_range": sal,
                        "contract_type": ctype,
                        "blue_card_eligible": blue_card,
                        "required_skills": skills,
                        "min_experience": exp,
                        "min_german_level": g_lvl,
                        "openings": openings,
                        "status": "Active",
                    }
                )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Job Listings"))

        # Candidate Resumes & Matches
        resumes_data = [
            ("Nikhil Ramesh", "nikhil.ramesh@example.com", "+91 98450 77112", "Germany", "Software & IT", 4, "B.Tech Computer Science", ["Kubernetes", "Docker", "Go", "AWS", "Linux"], "A2", "Fluent"),
            ("Anjali Kurup", "anjali.kurup@example.com", "+91 97451 88223", "Healthcare", "Healthcare", 3, "B.Sc Nursing", ["Patient Care", "ICU Support", "Medical Documentation"], "B2", "Good"),
        ]

        for cname, cemail, cphone, ctry, fld, exp, deg, skills, germ, eng in resumes_data:
            cand, _ = CandidateResume.objects.get_or_create(
                email=cemail,
                defaults={
                    "candidate_name": cname,
                    "phone": cphone,
                    "target_country": ctry,
                    "field": fld,
                    "years_of_experience": exp,
                    "highest_degree": deg,
                    "primary_skills": skills,
                    "german_level": germ,
                    "english_level": eng,
                    "status": "Matched",
                }
            )
            # Create match
            first_job = JobListing.objects.filter(domain=fld).first()
            if first_job:
                JobMatch.objects.get_or_create(
                    candidate=cand,
                    job=first_job,
                    defaults={
                        "match_score": 88,
                        "matched_skills": skills[:3],
                        "status": "Shortlisted",
                    }
                )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Candidate Resumes and Job Matches"))

        # ----------------------------------------------------------------------
        # 4. REWARDS PLAN & INCENTIVES
        # ----------------------------------------------------------------------
        plans_data = [
            ("Bronze Consultant Plan", "Bronze Consultant", "₹3,000 / Referral", 50, 5, "Entry-level ambassador tier. Earn ₹3,000 cash and 50 points per enrolled student."),
            ("Silver Ambassador Plan", "Silver Ambassador", "₹6,000 / Referral", 100, 15, "Mid-tier milestone. Unlock 10% commission on fee packages and corporate subsidies."),
            ("Gold Strategic Partner Plan", "Gold Strategic Partner", "₹12,000 / Referral", 250, 30, "Senior partner tier. Includes domestic team retreat and revenue royalties."),
            ("Platinum Institutional Lead", "Platinum Institutional Lead", "₹25,000 / Referral", 500, 50, "Institutional Director status. Includes fully funded European Study Tour."),
        ]

        for pname, tier, bonus, pts, thresh, desc in plans_data:
            RewardPlan.objects.get_or_create(
                plan_name=pname,
                defaults={
                    "tier_level": tier,
                    "referral_bonus_cash": bonus,
                    "points_per_referral": pts,
                    "milestone_threshold": thresh,
                    "description": desc,
                    "status": "Active",
                }
            )

        rules_data = [
            ("Student Enrolled in German A1-B2 Language Track", "Referral", 50, "₹3,000 Direct Bank Transfer", "Awarded upon successful fee clearance of language batch enrollment."),
            ("Direct Public University Admission (Germany/EU)", "Referral", 150, "₹10,000 Milestone Payout", "Awarded upon student receipt of official admission letter and APS approval."),
            ("College Campus MoU Signed for Language Lab", "Institutional", 500, "₹25,000 Institutional Grant", "Awarded to campus ambassadors who facilitate institutional partnership agreements."),
            ("Goethe-Zertifikat B2 Exam Cleared by Candidate", "Course Milestone", 100, "₹5,000 Academic Excellence Subsidy", "Performance reward for candidates achieving 80%+ marks in official exams."),
        ]

        for act, cat, pts, cash, desc in rules_data:
            RewardRule.objects.get_or_create(
                action_title=act,
                defaults={
                    "category": cat,
                    "points_reward": pts,
                    "cash_incentive": cash,
                    "description": desc,
                    "status": "Active",
                }
            )

        catalog_items = [
            ("Apple iPad Air (M2) 128GB Wi-Fi (Academic Edition)", "Gift Package", 500, "₹62,000 Value", "Top Performer", "In Stock", "High-performance tablet designed for digital notes, interactive PDF study, and language apps."),
            ("Fully Funded Europe Exposure Trip (Munich & Berlin)", "Tour Package", 1500, "₹1,80,000 Value", "Exclusive", "Limited Availability", "7-Day fully sponsored tour including flights, 4-star accommodation, and visits to TU Munich and SAP HQ."),
            ("Complete German B2 Language Course Subsidy Voucher", "Course Subsidy", 250, "₹35,000 Value", "Essential", "In Stock", "100% tuition waiver for any live online Goethe/TELC B1-B2 preparation cohort."),
            ("Instant NEFT/IMPS Bank Transfer Cashback (₹10,000)", "Cashback", 100, "₹10,000 Bank Cash", "Instant Payout", "In Stock", "Direct bank cash transfer credited within 24 business hours."),
        ]

        for ititle, itype, cost, val, badge, stock, desc in catalog_items:
            RewardCatalogItem.objects.get_or_create(
                title=ititle,
                defaults={
                    "item_type": itype,
                    "points_cost": cost,
                    "monetary_value": val,
                    "badge": badge,
                    "stock_status": stock,
                    "description": desc,
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Reward Plans, Rules and Catalog Items"))

        # ----------------------------------------------------------------------
        # 5. COMMUNICATION ENGINE WORKFLOWS & LOGS
        # ----------------------------------------------------------------------
        workflows = [
            (
                "Instant Welcome & Portal Access on Registration",
                "student_registration",
                "Welcome & Onboarding",
                "WhatsApp",
                "Welcome to ILA Academy! Your Student Portal is Ready",
                "Guten Tag {{name}}! Welcome to ILA Global. Your application for {{course}} has been received. Your dedicated consultant is {{tutor}}. Access your roadmap: {{portal_link}}",
                0,
                "Zero-Latency Instant"
            ),
            (
                "Live Batch Orientation & Class 24h Countdown",
                "class_start_24h",
                "Class & Schedule Alerts",
                "Multi-Channel",
                "Reminder: Your Live Session Starts in 24 Hours",
                "Hello {{name}}, your live batch for {{course}} starts tomorrow at {{time}}. Please verify your microphone and textbook: {{portal_link}}",
                1440,
                "Schedule Sync"
            ),
            (
                "Drop-off Recovery: Incomplete Intake Application",
                "pending_enrollment_24h",
                "Enrollment Follow-ups",
                "WhatsApp",
                "Complete your Germany Pathway Application",
                "Hi {{name}}, we noticed you paused your application for {{course}}. Reserve your seat before batch closing: {{portal_link}}",
                120,
                "Retention AI"
            ),
            (
                "Fee Installment & Blocked Account Setup Reminder",
                "payment_reminder",
                "Payment & Retention",
                "Email",
                "Action Required: Fee Verification & Blocked Account Checklist",
                "Dear {{name}}, your admission approval for {{course}} is confirmed. Please finalize your deposit to lock your university seat: {{portal_link}}",
                60,
                "Finance Gate"
            ),
        ]

        for wname, tevent, cat, chan, subj, tmpl, delay, badge in workflows:
            wf, _ = CommunicationWorkflowRule.objects.get_or_create(
                name=wname,
                defaults={
                    "trigger_event": tevent,
                    "category": cat,
                    "channel": chan,
                    "subject": subj,
                    "message_template": tmpl,
                    "delay_minutes": delay,
                    "badge": badge,
                    "total_dispatched": 142,
                    "delivered_count": 139,
                    "opened_count": 128,
                    "failed_count": 3,
                    "is_active": True,
                }
            )

            # Sample Dispatch Log
            DispatchLog.objects.get_or_create(
                workflow=wf,
                recipient_name="Aditya Varma",
                defaults={
                    "id": f"LOG-{uuid.uuid4().hex[:6].upper()}",
                    "recipient_email": "aditya.varma@example.com",
                    "recipient_phone": "+91 98450 66554",
                    "course_or_batch": "German A1 Live Interactive",
                    "channel": chan if chan != "Multi-Channel" else "WhatsApp",
                    "status": "Delivered",
                    "message_preview": f"Guten Tag Aditya! Welcome to ILA Global. Access your roadmap: https://ilas.global/student-portal",
                    "latency_ms": 280,
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Communication Engine Workflow Rules and Dispatch Logs"))

        # ----------------------------------------------------------------------
        # 6. INTAKE TRACKING & DEPARTMENT CRM
        # ----------------------------------------------------------------------
        inquiries_data = [
            ("Education", "Online Funnel", "Pooja Hegde", "pooja.hegde@example.com", "+91 98210 11223", "German Language B1 Executive Sprint", "Looking for evening batches after 7 PM IST.", "Contacted"),
            ("Study Abroad", "Walk-in", "Gautam Krishna", "gautam.krishna@example.com", "+91 98450 33445", "TU Munich M.Sc. Data Engineering", "Has 8.4 CGPA in B.Tech CSE. Awaiting APS appointment.", "In-Review"),
            ("Jobs", "WhatsApp Direct", "Deepak Chawla", "deepak.chawla@example.com", "+91 99100 88776", "Chancenkarte Opportunity Card IT Pathway", "5 years experience in React & Java. Needs points evaluation.", "New"),
            ("Work While You Study", "Referral", "Shruti Pillai", "shruti.pillai@example.com", "+91 97451 22334", "Nursing Ausbildung Dual Apprenticeship", "B.Sc Nursing graduate with B1 German certificate.", "Enrolled"),
            ("Visa", "Online Funnel", "Rahul Sengupta", "rahul.sengupta@example.com", "+91 98110 55667", "National Student Visa Appointment & Mock Prep", "Blocked account opened via Expatrio. VFS slot booked.", "In-Review"),
        ]

        for dept, itype, iname, iemail, iphone, iprog, inotes, istat in inquiries_data:
            DepartmentInquiry.objects.get_or_create(
                email=iemail,
                department=dept,
                defaults={
                    "inquiry_type": itype,
                    "name": iname,
                    "phone": iphone,
                    "program_of_interest": iprog,
                    "notes": inotes,
                    "status": istat,
                    "counselor_assigned": "Meera Kapoor (Lead Counselor)",
                }
            )

        # Trigger Rules
        FollowUpAutoTriggerRule.objects.get_or_create(
            trigger_name="Auto WhatsApp Nudge: Missing APS Document",
            defaults={
                "department": "Study Abroad",
                "event_type": "document_pending",
                "channel": "WhatsApp",
                "delay_hours": 4,
                "message_template": "Hi {name}, please upload your university degree transcript to proceed with your German admission.",
                "is_active": True,
                "execution_count": 86,
            }
        )

        # Social Campaigns
        SocialMediaCampaign.objects.get_or_create(
            title="German Chancenkarte Opportunity Card - Fast Track Corridor 2026",
            defaults={
                "department": "Jobs",
                "content": "Work in Germany with the new Opportunity Card visa. Pre-screen your points score with ILA Academy.",
                "channels": ["Meta Ads", "LinkedIn", "Instagram"],
                "target_audience": "Engineers, IT Professionals, Nurses in India",
                "status": "Published",
                "reach_count": 48200,
                "clicks_count": 3120,
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Department Intake CRM and Social Campaigns"))

        self.stdout.write("==================================================")
        self.stdout.write(self.style.SUCCESS("*** ALL ILA_WEB_NEW SUBSYSTEMS FULLY INITIALIZED & SEEDED ***"))
        self.stdout.write("==================================================")
