import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from Applications.CorporateAdmin.models import (
    Organization, Branch, Department, Team, Profile, Role, Permission, RolePermission,
    Employee, Inquiry, Lead, Opportunity, Candidate, Onboarding,
    Task, TaskComment, Approval, Expense, Campaign, Notification, AuditLog,
    EntityStatus, BranchStatus, RoleCode, EmploymentType, EmploymentStatus,
    InquirySource, InquiryPriority, InquiryStatus, LeadStatus, OpportunityStage,
    CandidateStage, OnboardingStatus, DocumentationStatus, ApprovalStatus,
    TaskPriority, TaskStatus, ApprovalType, CampaignStatus, ExpenseStatus,
    NotificationType
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed enterprise demonstration data for CentelizedDashboard (ILA Admin Command Center)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding CentelizedDashboard data..."))

        # 1. Organization
        org, created = Organization.objects.get_or_create(
            code="GEG-CORP",
            defaults={
                "name": "Global Enterprise Group (GEG)",
                "description": "Primary multi-national conglomerate and centralized command center headquarters",
                "logo_url": "https://images.unsplash.com/photo-1554469384-e58fac16e23a?w=400",
                "status": EntityStatus.ACTIVE
            }
        )
        self.stdout.write(f"  [Organization] {org.name} ({org.code})")

        # 2. Branches
        hq, _ = Branch.objects.get_or_create(
            organization=org,
            code="HQ-DUB",
            defaults={"name": "Dubai Global Headquarters", "location": "DIFC Gate Tower, Dubai, UAE", "status": BranchStatus.ACTIVE}
        )
        sg_branch, _ = Branch.objects.get_or_create(
            organization=org,
            code="APAC-SG",
            defaults={"name": "Singapore Innovation Hub", "location": "Marina Bay Financial Centre, Singapore", "status": BranchStatus.ACTIVE}
        )

        # 3. Permissions
        modules = ['ORGANIZATION', 'HR', 'FINANCE', 'CRM', 'RECRUITMENT', 'ONBOARDING', 'TASKS', 'APPROVALS', 'ANALYTICS']
        actions = ['READ', 'WRITE', 'DELETE', 'APPROVE']
        all_perms = []
        for mod in modules:
            for act in actions:
                p, _ = Permission.objects.get_or_create(
                    module=mod,
                    action=act,
                    defaults={"description": f"Allow {act} on {mod} module"}
                )
                all_perms.append(p)

        # 4. Roles
        roles_spec = [
            (RoleCode.SUPER_ADMIN, "Super Administrator", 1),
            (RoleCode.CEO, "Chief Executive Officer", 2),
            (RoleCode.HR_MANAGER, "HR Director & Manager", 3),
            (RoleCode.FINANCE_MANAGER, "Finance Director", 3),
            (RoleCode.SALES_MANAGER, "Global Sales Director", 3),
            (RoleCode.OPERATIONS_MANAGER, "Chief Operations Manager", 3),
            (RoleCode.TEAM_LEAD, "Engineering & Ops Team Lead", 5),
            (RoleCode.EMPLOYEE, "Staff & Enterprise Employee", 10),
        ]
        roles_dict = {}
        for code, disp, lvl in roles_spec:
            r, _ = Role.objects.get_or_create(
                name=code,
                defaults={"display_name": disp, "level": lvl, "description": f"{disp} role permissions"}
            )
            roles_dict[code] = r
            if code in [RoleCode.SUPER_ADMIN, RoleCode.CEO]:
                for perm in all_perms:
                    RolePermission.objects.get_or_create(role=r, permission=perm)

        # 5. Departments
        dept_spec = [
            ("DEP-EXEC", "Executive Leadership", Decimal("500000.00")),
            ("DEP-HR", "Human Resources & Talent", Decimal("250000.00")),
            ("DEP-FIN", "Corporate Finance & Treasury", Decimal("750000.00")),
            ("DEP-SALES", "Commercial Sales & Growth", Decimal("400000.00")),
            ("DEP-OPS", "Global Operations & Logistics", Decimal("600000.00")),
            ("DEP-ENG", "Technology & Systems", Decimal("800000.00")),
        ]
        dept_dict = {}
        for d_code, d_name, d_budget in dept_spec:
            d, _ = Department.objects.get_or_create(
                organization=org,
                code=d_code,
                defaults={"name": d_name, "budget": d_budget, "status": BranchStatus.ACTIVE}
            )
            dept_dict[d_code] = d

        # 6. Teams
        team_ops, _ = Team.objects.get_or_create(
            department=dept_dict["DEP-OPS"],
            name="Command Dispatch Alpha",
            defaults={"description": "24/7 global operations mission control"}
        )
        team_sales, _ = Team.objects.get_or_create(
            department=dept_dict["DEP-SALES"],
            name="Enterprise Strategic Accounts",
            defaults={"description": "High-value multinational procurement accounts"}
        )

        # 7. Seed Staff Profiles & Employees
        employees_spec = [
            ("EMP-001", "Marcus Vance", "marcus.vance@ila-command.com", "+971-50-1234567", "Chief Executive Officer", RoleCode.CEO, "DEP-EXEC", Decimal("25000.00")),
            ("EMP-002", "Sarah Connor", "sarah.connor@ila-command.com", "+971-50-2345678", "VP Human Capital", RoleCode.HR_MANAGER, "DEP-HR", Decimal("15000.00")),
            ("EMP-003", "David Sterling", "david.sterling@ila-command.com", "+971-50-3456789", "Chief Financial Officer", RoleCode.FINANCE_MANAGER, "DEP-FIN", Decimal("18000.00")),
            ("EMP-004", "Elena Rostova", "elena.rostova@ila-command.com", "+971-50-4567890", "Head of Global Sales", RoleCode.SALES_MANAGER, "DEP-SALES", Decimal("16000.00")),
            ("EMP-005", "Tariq Mansour", "tariq.mansour@ila-command.com", "+971-50-5678901", "Director of Operations", RoleCode.OPERATIONS_MANAGER, "DEP-OPS", Decimal("14000.00")),
            ("EMP-006", "Lucas Wright", "lucas.wright@ila-command.com", "+971-50-6789012", "Senior Enterprise Executive", RoleCode.EMPLOYEE, "DEP-SALES", Decimal("9500.00")),
        ]
        emp_dict = {}
        for emp_code, name, email, phone, desig, r_code, d_code, salary in employees_spec:
            user_obj, _ = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "is_staff": True}
            )
            user_obj.set_password("Admin@123456")
            user_obj.save()

            prof, _ = Profile.objects.get_or_create(
                email=email,
                defaults={
                    "user": user_obj,
                    "full_name": name,
                    "phone": phone,
                    "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={emp_code}",
                    "status": EntityStatus.ACTIVE
                }
            )

            emp, _ = Employee.objects.get_or_create(
                employee_code=emp_code,
                defaults={
                    "profile": prof,
                    "organization": org,
                    "department": dept_dict[d_code],
                    "role": roles_dict[r_code],
                    "designation": desig,
                    "salary": salary,
                    "employment_type": EmploymentType.FULL_TIME,
                    "employment_status": EmploymentStatus.ACTIVE
                }
            )
            emp_dict[emp_code] = emp

        # Assign managers and department heads
        dept_dict["DEP-EXEC"].department_head = emp_dict["EMP-001"]
        dept_dict["DEP-EXEC"].save()
        dept_dict["DEP-HR"].department_head = emp_dict["EMP-002"]
        dept_dict["DEP-HR"].save()
        dept_dict["DEP-FIN"].department_head = emp_dict["EMP-003"]
        dept_dict["DEP-FIN"].save()
        dept_dict["DEP-SALES"].department_head = emp_dict["EMP-004"]
        dept_dict["DEP-SALES"].save()
        dept_dict["DEP-OPS"].department_head = emp_dict["EMP-005"]
        dept_dict["DEP-OPS"].save()

        emp_dict["EMP-006"].manager = emp_dict["EMP-004"]
        emp_dict["EMP-006"].team = team_sales
        emp_dict["EMP-006"].save()

        # 8. Inquiries
        Inquiry.objects.get_or_create(
            name="Apex Horizon Trading",
            phone="+971-4-8889900",
            organization=org,
            defaults={
                "email": "procurement@apexhorizon.com",
                "source": InquirySource.WEBSITE,
                "assigned_to": emp_dict["EMP-006"],
                "department": dept_dict["DEP-SALES"],
                "priority": InquiryPriority.HIGH,
                "status": InquiryStatus.IN_PROGRESS,
                "notes": "Requesting quote for commodity logistics escrow services."
            }
        )

        # 9. Leads & Opportunities
        lead1, _ = Lead.objects.get_or_create(
            name="Dr. Aris Thorne",
            company="Thorne Petrochemicals AG",
            organization=org,
            defaults={
                "email": "a.thorne@thornepetrochemicals.com",
                "phone": "+41-22-7788990",
                "source": "SWISS INDUSTRIAL EXPO",
                "assigned_to": emp_dict["EMP-006"],
                "department": dept_dict["DEP-SALES"],
                "interested_product": "Escrow Logistics & Multimodal Transport",
                "estimated_value": Decimal("1500000.00"),
                "priority": InquiryPriority.URGENT,
                "status": LeadStatus.QUALIFIED
            }
        )

        Opportunity.objects.get_or_create(
            lead=lead1,
            organization=org,
            title="Thorne Global Supply Chain Contract",
            defaults={
                "value": Decimal("1500000.00"),
                "stage": OpportunityStage.PROPOSAL,
                "assigned_to": emp_dict["EMP-006"],
                "probability": 70,
                "close_date": timezone.now().date() + timezone.timedelta(days=30)
            }
        )

        # 10. Candidates & Onboarding
        cand1, _ = Candidate.objects.get_or_create(
            full_name="Liam Chen",
            email="liam.chen@talentpool.io",
            organization=org,
            defaults={
                "phone": "+65-8123-4567",
                "position": "Principal Distributed Systems Architect",
                "department": dept_dict["DEP-ENG"],
                "stage": CandidateStage.ONBOARDING,
                "expected_salary": Decimal("18000.00"),
                "notes": "Top tier candidate with 12 years FinTech distributed ledger experience."
            }
        )

        Onboarding.objects.get_or_create(
            candidate=cand1,
            organization=org,
            defaults={
                "department": dept_dict["DEP-ENG"],
                "manager": emp_dict["EMP-005"],
                "status": OnboardingStatus.IN_PROGRESS,
                "progress": 65,
                "current_step": "EQUIPMENT_PROVISIONING",
                "documentation_status": DocumentationStatus.VERIFIED,
                "approval_status": ApprovalStatus.APPROVED,
                "checklist": [
                    {"id": "c1", "title": "Passport & Visa Verification", "completed": True},
                    {"id": "c2", "title": "Hardware specs confirmed & issued", "completed": True},
                    {"id": "c3", "title": "VPN & Access Token Provisioning", "completed": False},
                    {"id": "c4", "title": "Team Introductory Welcome Call", "completed": False}
                ]
            }
        )

        # 11. Tasks & Comments
        task1, _ = Task.objects.get_or_create(
            title="Finalize Q4 Global Escrow Audit Review",
            organization=org,
            defaults={
                "description": "Consolidate international multi-currency escrow accounts with external Big-4 auditors.",
                "created_by": emp_dict["EMP-001"],
                "assigned_to": emp_dict["EMP-003"],
                "department": dept_dict["DEP-FIN"],
                "priority": TaskPriority.URGENT,
                "status": TaskStatus.IN_PROGRESS,
                "due_date": timezone.now() + timezone.timedelta(days=7)
            }
        )

        TaskComment.objects.get_or_create(
            task=task1,
            author=emp_dict["EMP-003"],
            defaults={"comment": "First draft of ledger reconciliation is ready for CFO sign-off."}
        )

        # 12. Approvals
        Approval.objects.get_or_create(
            requester=emp_dict["EMP-004"],
            request_type=ApprovalType.EXPENSE,
            organization=org,
            defaults={
                "approver": emp_dict["EMP-003"],
                "amount": Decimal("4800.00"),
                "status": ApprovalStatus.PENDING,
                "justification": "International client travel & delegation hospitality expenses in Zurich."
            }
        )

        # 13. Expenses
        Expense.objects.get_or_create(
            title="Q3 Core Cloud Infrastructure & CDN",
            organization=org,
            defaults={
                "department": dept_dict["DEP-ENG"],
                "requester": emp_dict["EMP-005"],
                "category": "INFRASTRUCTURE",
                "amount": Decimal("24500.00"),
                "status": ExpenseStatus.PAID
            }
        )

        # 14. Campaigns
        Campaign.objects.get_or_create(
            name="Global Trade Escrow Expansion 2026",
            organization=org,
            defaults={
                "description": "Targeted B2B campaign across Mediterranean & GCC trade corridors",
                "status": CampaignStatus.ACTIVE,
                "budget": Decimal("85000.00"),
                "spent": Decimal("32400.00"),
                "leads_generated": 142,
                "start_date": timezone.now().date() - timezone.timedelta(days=20),
                "end_date": timezone.now().date() + timezone.timedelta(days=70)
            }
        )

        # 15. Notifications
        Notification.objects.get_or_create(
            user=emp_dict["EMP-001"].profile,
            title="Executive Approval Pending",
            defaults={
                "message": "Sales team requested $4,800.00 travel reimbursement for Zurich conference.",
                "type": NotificationType.APPROVAL,
                "priority": "HIGH",
                "is_read": False
            }
        )

        # 16. Audit Log
        AuditLog.objects.get_or_create(
            organization=org,
            action="ORGANIZATION_INITIALIZED",
            module="CORE",
            entity_type="Organization",
            entity_id=org.id,
            defaults={
                "user": emp_dict["EMP-001"].profile,
                "user_name": "Marcus Vance",
                "new_data": {"name": org.name, "code": org.code, "status": org.status}
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded CentelizedDashboard demo data!"))
