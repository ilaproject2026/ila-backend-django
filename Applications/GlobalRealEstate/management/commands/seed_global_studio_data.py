import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from Applications.GlobalRealEstate.models import (
    Landlord,
    MasterLease,
    Property,
    Room,
    TenantUser,
    DocumentRecord,
    PlacedTenantReferral,
    ProfitShareLedgerEntry,
    DutyRosterTask,
    HygienePenalty,
    ERPInvoice,
    ERPStaff,
    ERPKanbanTask,
    MaintenanceTicket,
    BrokerRecord,
    MarketingCampaign,
    CommercialDeal,
    SupplyProduct,
    ComplianceItem,
    ExpansionHubKPI,
)


class Command(BaseCommand):
    help = 'Seeds database with worldwide co-living properties, resident Marcus Vance, and ERP data for Global Studio'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding ILA Global Real Estate & Co-Living database...")

        # ----------------------------------------------------------------------
        # 1. Seed Landlords
        # ----------------------------------------------------------------------
        ll_frankfurt, _ = Landlord.objects.update_or_create(
            email="h.braun@braun-frankfurt.de",
            defaults={
                "full_name": "Helmut Braun",
                "company_name": "Helmut Braun Immobilien GmbH",
                "phone": "+49 69 4432 901",
                "country": "Germany",
            }
        )

        ll_london, _ = Landlord.objects.update_or_create(
            email="charles.windsor@kensington-trust.co.uk",
            defaults={
                "full_name": "Charles Windsor",
                "company_name": "Kensington Real Estate Trust",
                "phone": "+44 20 7946 0912",
                "country": "United Kingdom",
            }
        )

        ll_dubai, _ = Landlord.objects.update_or_create(
            email="invest@emaar-partners.ae",
            defaults={
                "full_name": "Rashid Al Maktoum",
                "company_name": "Emaar Institutional Custody",
                "phone": "+971 4 367 3333",
                "country": "United Arab Emirates",
            }
        )

        # ----------------------------------------------------------------------
        # 2. Seed Master Leases & Properties
        # ----------------------------------------------------------------------
        # A. Frankfurt Flagship
        ffm_lease, _ = MasterLease.objects.update_or_create(
            generated_property_uid="GLB-FFM-BLD1",
            defaults={
                "landlord": ll_frankfurt,
                "landlord_name": "Helmut Braun Immobilien GmbH",
                "landlord_email": "h.braun@braun-frankfurt.de",
                "landlord_phone": "+49 69 4432 901",
                "building_name": "ILA Grand Central Skyline Hub",
                "city_code": "FFM",
                "city_name": "Frankfurt",
                "country": "Germany",
                "address": "Mainzer Landstraße 180, 60327 Frankfurt am Main",
                "total_floors": 6,
                "total_capacity": 18,
                "monthly_master_rent": Decimal("7800.00"),
                "currency": "EUR",
                "lease_start_date": datetime.date(2025, 1, 1),
                "lease_end_date": datetime.date(2030, 12, 31),
                "status": "ACTIVE",
            }
        )

        ffm_prop, _ = Property.objects.update_or_create(
            property_uid="GLB-FFM-BLD1",
            defaults={
                "master_lease": ffm_lease,
                "title": "ILA Grand Central Skyline Hub",
                "city": "Frankfurt",
                "city_code": "FFM",
                "country": "Germany",
                "neighborhood": "Westend / Financial Quarter",
                "address": "Mainzer Landstraße 180",
                "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1000&q=80",
                "images": [
                    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80"
                ],
                "amenities": [
                    "Gigabit Fiber WiFi", "Soundproof Podcast Studio", "Bi-Weekly Deep Hygiene",
                    "Coworking Desks", "Smart Card Access", "Rooftop Skyline Terrace"
                ],
                "total_rooms": 18,
                "active_occupancy": 16,
                "featured": True,
                "syndication_active": True,
                "total_valuation": Decimal("1850000.00"),
                "co_invest_target": Decimal("450000.00"),
                "co_invest_raised": Decimal("385000.00"),
                "projected_roi_pct": Decimal("16.40"),
                "description": (
                    "Flagship European co-living asset in the heart of Frankfurt's banking district. "
                    "Engineered with 18 fully furnished micro-studios, high-speed fiber connectivity, "
                    "and automated growth-loop profit sharing."
                )
            }
        )

        # Generate Rooms for Frankfurt
        for i in range(1, 19):
            room_uid = f"GLB-FFM-BLD1-RM{i}"
            room_type = "Private Ensuite" if i <= 6 else ("Co-Living Studio" if i <= 14 else "Micro-Pod Suite")
            Room.objects.update_or_create(
                room_uid=room_uid,
                defaults={
                    "property": ffm_prop,
                    "room_number": f"{100 + i}",
                    "room_type": room_type,
                    "sqm": Decimal(str(16 + (i % 4) * 3)),
                    "regular_rent_amount": Decimal(str(460 + (i % 3) * 40)),
                    "micro_investor_rent_amount": Decimal(str(330 + (i % 3) * 35)),
                    "security_deposit_amount": Decimal("450.00"),
                    "currency": "EUR",
                    "is_available": i > 16,
                    "floor": (i // 4) + 1,
                    "features": ["High-speed WiFi", "Acoustic Insulation", "Ergonomic Desk", "Smart Lock"],
                }
            )

        # B. London Tech Quarter
        ldn_lease, _ = MasterLease.objects.update_or_create(
            generated_property_uid="GLB-LDN-BLD1",
            defaults={
                "landlord": ll_london,
                "landlord_name": "Kensington Real Estate Trust",
                "landlord_email": "charles.windsor@kensington-trust.co.uk",
                "landlord_phone": "+44 20 7946 0912",
                "building_name": "ILA Kensington Innovation Hub",
                "city_code": "LDN",
                "city_name": "London",
                "country": "United Kingdom",
                "address": "42 Cromwell Road, South Kensington, London SW7",
                "total_floors": 5,
                "total_capacity": 12,
                "monthly_master_rent": Decimal("9200.00"),
                "currency": "GBP",
                "lease_start_date": datetime.date(2025, 2, 1),
                "lease_end_date": datetime.date(2031, 1, 31),
                "status": "ACTIVE",
            }
        )

        ldn_prop, _ = Property.objects.update_or_create(
            property_uid="GLB-LDN-BLD1",
            defaults={
                "master_lease": ldn_lease,
                "title": "ILA Kensington Innovation Hub",
                "city": "London",
                "city_code": "LDN",
                "country": "United Kingdom",
                "neighborhood": "South Kensington / Imperial Corridor",
                "address": "42 Cromwell Road, SW7",
                "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
                "images": [
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80"
                ],
                "amenities": ["Superfast Broadband", "Private Meeting Booths", "Weekly Housekeeping", "Tube Station 2 Min"],
                "total_rooms": 12,
                "active_occupancy": 11,
                "featured": True,
                "syndication_active": True,
                "total_valuation": Decimal("2400000.00"),
                "co_invest_target": Decimal("600000.00"),
                "co_invest_raised": Decimal("520000.00"),
                "projected_roi_pct": Decimal("15.80"),
                "description": "High-yield London micro-living asset near Imperial College and South Kensington cultural quarter."
            }
        )

        for i in range(1, 13):
            room_uid = f"GLB-LDN-BLD1-RM{i}"
            Room.objects.update_or_create(
                room_uid=room_uid,
                defaults={
                    "property": ldn_prop,
                    "room_number": f"{200 + i}",
                    "room_type": "Private Ensuite" if i % 2 == 0 else "Co-Living Studio",
                    "sqm": Decimal("20.00"),
                    "regular_rent_amount": Decimal("680.00"),
                    "micro_investor_rent_amount": Decimal("490.00"),
                    "security_deposit_amount": Decimal("680.00"),
                    "currency": "GBP",
                    "is_available": i == 12,
                    "floor": (i // 3) + 1,
                    "features": ["Ensuite Bathroom", "Designer Desk", "Fiber Optic Line"],
                }
            )

        # C. Dubai Marina Hub
        dxb_lease, _ = MasterLease.objects.update_or_create(
            generated_property_uid="GLB-DXB-BLD1",
            defaults={
                "landlord": ll_dubai,
                "landlord_name": "Emaar Institutional Custody",
                "landlord_email": "invest@emaar-partners.ae",
                "landlord_phone": "+971 4 367 3333",
                "building_name": "ILA Marina Tech Tower",
                "city_code": "DXB",
                "city_name": "Dubai",
                "country": "United Arab Emirates",
                "address": "Marina Promenade Tower 2, Dubai Marina",
                "total_floors": 8,
                "total_capacity": 14,
                "monthly_master_rent": Decimal("14500.00"),
                "currency": "AED",
                "lease_start_date": datetime.date(2025, 3, 1),
                "lease_end_date": datetime.date(2030, 2, 28),
                "status": "ACTIVE",
            }
        )

        dxb_prop, _ = Property.objects.update_or_create(
            property_uid="GLB-DXB-BLD1",
            defaults={
                "master_lease": dxb_lease,
                "title": "ILA Marina Tech Tower Residence",
                "city": "Dubai",
                "city_code": "DXB",
                "country": "United Arab Emirates",
                "neighborhood": "Dubai Marina / JBR Beach",
                "address": "Marina Promenade Tower 2",
                "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80",
                "images": [
                    "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80"
                ],
                "amenities": ["Infinity Marina Pool", "Valet Concierge", "High-Speed Mesh WiFi", "Gym & Sauna"],
                "total_rooms": 14,
                "active_occupancy": 13,
                "featured": True,
                "syndication_active": True,
                "total_valuation": Decimal("3100000.00"),
                "co_invest_target": Decimal("750000.00"),
                "co_invest_raised": Decimal("690000.00"),
                "projected_roi_pct": Decimal("18.20"),
                "description": "Tax-free digital nomad and investor residency suites overlooking Dubai Marina."
            }
        )

        # ----------------------------------------------------------------------
        # 3. Seed Resident Tenant User (Marcus Vance)
        # ----------------------------------------------------------------------
        marcus_room = Room.objects.filter(property=ffm_prop, room_number="103").first()
        marcus, _ = TenantUser.objects.update_or_create(
            email="marcus.vance@ila-global.com",
            defaults={
                "full_name": "Marcus Vance",
                "phone": "+49 176 9821 443",
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                "role": "MICRO_INVESTOR",
                "option_type": "OPTION_B",
                "assigned_property": ffm_prop,
                "assigned_room": marcus_room,
                "assigned_room_uid": "GLB-FFM-BLD1-RM3",
                "property_title": "ILA Grand Central Skyline Hub",
                "city": "Frankfurt",
                "lease_start_date": datetime.date(2025, 1, 15),
                "lease_end_date": datetime.date(2026, 1, 14),
                "monthly_rent_charged": Decimal("330.00"),
                "deposit_held": Decimal("450.00"),
                "wallet_balance": Decimal("1450.00"),
                "total_micro_invested": Decimal("8500.00"),
                "active_profit_share_tier": "Gold (30%)",
                "active_commission_pct": Decimal("30.00"),
                "referral_code": "ILA-VANCE-98",
                "hygiene_score": 96,
            }
        )

        # Documents for Marcus
        docs = [
            {"doc_type": "ID_PASSPORT", "title": "EU Identity Document", "file_name": "passport_vance_verified.pdf", "verified": True},
            {"doc_type": "PROOF_OF_FUNDS", "title": "Income & Bank Verification", "file_name": "deutsche_bank_income.pdf", "verified": True},
            {"doc_type": "LEASE_AGREEMENT", "title": "Co-Living Micro-Investor Lease", "file_name": "lease_contract_glb_ffm_rm3.pdf", "verified": True},
        ]
        for doc in docs:
            DocumentRecord.objects.update_or_create(
                tenant=marcus,
                doc_type=doc["doc_type"],
                defaults=doc
            )

        # Referrals placed by Marcus
        referrals = [
            {
                "placed_tenant_name": "Liam Berg",
                "placed_property_title": "ILA Grand Central Skyline Hub",
                "placed_room_uid": "GLB-FFM-BLD1-RM7",
                "monthly_rent": Decimal("460.00"),
                "status": "OCCUPIED_PAYING",
                "commission_tier_pct": Decimal("30.00"),
                "monthly_profit_share_earned": Decimal("138.00"),
                "placed_date": datetime.date(2025, 2, 1),
            },
            {
                "placed_tenant_name": "Sophia Chen",
                "placed_property_title": "ILA Grand Central Skyline Hub",
                "placed_room_uid": "GLB-FFM-BLD1-RM11",
                "monthly_rent": Decimal("480.00"),
                "status": "OCCUPIED_PAYING",
                "commission_tier_pct": Decimal("30.00"),
                "monthly_profit_share_earned": Decimal("144.00"),
                "placed_date": datetime.date(2025, 2, 15),
            }
        ]
        for ref in referrals:
            PlacedTenantReferral.objects.update_or_create(
                referring_tenant=marcus,
                placed_tenant_name=ref["placed_tenant_name"],
                defaults=ref
            )

        # Profit Ledger entries
        ledgers = [
            {
                "date": datetime.date(2025, 2, 1),
                "transaction_type": "RESIDUAL_PROFIT_YIELD",
                "amount": Decimal("282.00"),
                "currency": "EUR",
                "description": "Monthly Residual Profit Share: 2 Placed Tenants (30% Tier)",
                "status": "COMPLETED"
            },
            {
                "date": datetime.date(2025, 2, 15),
                "transaction_type": "GROWTH_LOOP_BONUS",
                "amount": Decimal("250.00"),
                "currency": "EUR",
                "description": "Growth Loop Relocation Bonus for placing Sophia Chen",
                "status": "COMPLETED"
            },
            {
                "date": datetime.date(2025, 3, 1),
                "transaction_type": "RESIDUAL_PROFIT_YIELD",
                "amount": Decimal("282.00"),
                "currency": "EUR",
                "description": "Monthly Residual Profit Share: Active Portfolio Distribution",
                "status": "COMPLETED"
            }
        ]
        for led in ledgers:
            ProfitShareLedgerEntry.objects.update_or_create(
                tenant=marcus,
                date=led["date"],
                transaction_type=led["transaction_type"],
                defaults=led
            )

        # ----------------------------------------------------------------------
        # 4. Seed Duty Rosters & Penalties
        # ----------------------------------------------------------------------
        today = datetime.date.today()
        roster_tasks = [
            {
                "property": ffm_prop,
                "property_title": ffm_prop.title,
                "tenant": marcus,
                "tenant_name": marcus.full_name,
                "tenant_avatar": marcus.avatar_url,
                "assigned_zone": "Main Kitchen & Waste Segregation",
                "scheduled_date": today + datetime.timedelta(days=1),
                "day_of_week": (today + datetime.timedelta(days=1)).strftime("%A"),
                "due_time": "22:00",
                "status": "PENDING",
            },
            {
                "property": ffm_prop,
                "property_title": ffm_prop.title,
                "tenant": marcus,
                "tenant_name": marcus.full_name,
                "tenant_avatar": marcus.avatar_url,
                "assigned_zone": "Coworking Lounge & Whiteboards",
                "scheduled_date": today - datetime.timedelta(days=6),
                "day_of_week": (today - datetime.timedelta(days=6)).strftime("%A"),
                "due_time": "22:00",
                "status": "APPROVED",
                "photo_proof_url": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=600&q=80",
                "submitted_at": "02/03/2026 21:15",
                "reviewed_by": "Liam Berg",
                "review_notes": "Immaculate standard. Countertops and floor pristine."
            },
        ]
        for task in roster_tasks:
            DutyRosterTask.objects.update_or_create(
                tenant=marcus,
                assigned_zone=task["assigned_zone"],
                scheduled_date=task["scheduled_date"],
                defaults=task
            )

        # ----------------------------------------------------------------------
        # 5. Seed 12-Module Enterprise ERP Records
        # ----------------------------------------------------------------------
        invoices = [
            {
                "invoice_number": "INV-2026-0812",
                "recipient_name": "Helmut Braun Immobilien GmbH",
                "recipient_email": "h.braun@braun-frankfurt.de",
                "property_uid": "GLB-FFM-BLD1",
                "amount": Decimal("7800.00"),
                "currency": "EUR",
                "category": "Master Lease Rent",
                "issue_date": datetime.date(2026, 3, 1),
                "due_date": datetime.date(2026, 3, 5),
                "status": "PAID"
            },
            {
                "invoice_number": "INV-2026-0813",
                "recipient_name": "Vodafone Gigabit Enterprise",
                "recipient_email": "billing@vodafone.de",
                "property_uid": "GLB-FFM-BLD1",
                "amount": Decimal("480.00"),
                "currency": "EUR",
                "category": "Fiber Internet Utility",
                "issue_date": datetime.date(2026, 3, 1),
                "due_date": datetime.date(2026, 3, 15),
                "status": "PAID"
            }
        ]
        for inv in invoices:
            ERPInvoice.objects.update_or_create(
                invoice_number=inv["invoice_number"],
                defaults=inv
            )

        staff_members = [
            {
                "name": "Elena Rostova",
                "role": "Central European Community Director",
                "department": "Community & Tenant Operations",
                "hub": "Frankfurt / DACH",
                "email": "e.rostova@ila-global.com",
                "phone": "+49 69 9821 550",
                "active_tasks_count": 8,
                "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80"
            },
            {
                "name": "Klaus Lindemann",
                "role": "Head of Property Maintenance & Smart IoT",
                "department": "Facility & Engineering",
                "hub": "Frankfurt / DACH",
                "email": "k.lindemann@ila-global.com",
                "phone": "+49 69 9821 552",
                "active_tasks_count": 5,
                "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"
            }
        ]
        for st in staff_members:
            ERPStaff.objects.update_or_create(
                email=st["email"],
                defaults=st
            )

        kanban_tasks = [
            {
                "title": "Smart Lock Firmware & Keycard Sync",
                "description": "Deploy rolling encryption update to all 18 room locks in GLB-FFM-BLD1.",
                "assigned_to_name": "Klaus Lindemann",
                "department": "Facility & Engineering",
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "property_uid": "GLB-FFM-BLD1",
                "due_date": today + datetime.timedelta(days=2),
            },
            {
                "title": "Bi-Weekly Deep Cleaning Inspection",
                "description": "Verify communal kitchen sanitation and terrace maintenance.",
                "assigned_to_name": "Elena Rostova",
                "department": "Community & Tenant Operations",
                "priority": "MEDIUM",
                "status": "TODO",
                "property_uid": "GLB-FFM-BLD1",
                "due_date": today + datetime.timedelta(days=4),
            }
        ]
        for kt in kanban_tasks:
            ERPKanbanTask.objects.update_or_create(
                title=kt["title"],
                defaults=kt
            )

        MaintenanceTicket.objects.update_or_create(
            ticket_code="TKT-4921",
            defaults={
                "property_uid": "GLB-FFM-BLD1",
                "room_uid": "GLB-FFM-BLD1-RM4",
                "tenant_name": "Liam Berg",
                "category": "Plumbing",
                "title": "Ensuite Shower Pressure Valve Calibration",
                "description": "Shower head pressure slightly below standard after municipal grid check.",
                "priority": "MEDIUM",
                "status": "DISPATCHED",
                "assigned_contractor": "Frankfurt Sanitär Express GmbH",
                "cost_estimate": Decimal("140.00"),
                "logged_date": today - datetime.timedelta(days=1),
            }
        )

        BrokerRecord.objects.update_or_create(
            referral_code="BRK-BER-SAVILLS",
            defaults={
                "name": "Sarah Jenkins",
                "agency": "Savills European Residential",
                "email": "sjenkins@savills.de",
                "phone": "+49 30 7261 6500",
                "total_placements": 14,
                "total_commission_paid": Decimal("6800.00"),
                "pending_payout": Decimal("1200.00"),
                "commission_rate_pct": Decimal("10.00"),
                "status": "ACTIVE"
            }
        )

        MarketingCampaign.objects.update_or_create(
            title="DACH Young Tech Professionals & Fintech Relocation",
            defaults={
                "channel": "LinkedIn Ads & Expat Communities",
                "target_segment": "Software Engineers, Analysts, Remote Founders",
                "target_city": "Frankfurt & London",
                "budget": Decimal("3500.00"),
                "leads_generated": 84,
                "conversions": 16,
                "status": "ACTIVE"
            }
        )

        CommercialDeal.objects.update_or_create(
            deal_code="CD-FFM-2026",
            defaults={
                "title": "Frankfurt Ostend Heritage Conversion (45 Beds)",
                "city": "Frankfurt",
                "country": "Germany",
                "floors": 7,
                "potential_rooms": 45,
                "total_acquisition_cost": Decimal("4800000.00"),
                "syndication_target": Decimal("1200000.00"),
                "syndication_raised": Decimal("750000.00"),
                "expected_cap_rate_pct": Decimal("6.80"),
                "projected_annual_yield_pct": Decimal("17.40"),
                "status": "STRUCTURING",
                "timeline": "Q3 2026 Turnkey Launch"
            }
        )

        SupplyProduct.objects.update_or_create(
            sku="ILA-SUP-TOWEL-01",
            defaults={
                "name": "ILA Signature Organic Micro-Cotton Towel Set",
                "category": "Room Linens",
                "unit_price": Decimal("24.50"),
                "in_stock": 85,
                "reorder_point": 20,
                "status": "IN_STOCK"
            }
        )

        ComplianceItem.objects.update_or_create(
            property_uid="GLB-FFM-BLD1",
            regulation_type="German Co-Living & Subletting Compliance (§540 BGB)",
            defaults={
                "jurisdiction": "State of Hesse / City of Frankfurt",
                "status": "COMPLIANT",
                "next_audit_date": datetime.date(2026, 9, 15),
                "legal_counsel": "Gleiss Lutz Rechtsanwälte Frankfurt",
                "notes": "Full commercial master lease with explicit co-living and micro-syndication rights."
            }
        )

        hubs = [
            {"city": "Frankfurt", "country": "Germany", "region": "Central Europe", "active_properties": 2, "total_beds": 36, "occupancy_rate_pct": Decimal("94.50"), "monthly_revenue_eur": Decimal("28500.00"), "expansion_target_beds": 120, "growth_potential": "HIGH"},
            {"city": "London", "country": "United Kingdom", "region": "Western Europe", "active_properties": 1, "total_beds": 12, "occupancy_rate_pct": Decimal("91.60"), "monthly_revenue_eur": Decimal("16200.00"), "expansion_target_beds": 80, "growth_potential": "VERY_HIGH"},
            {"city": "Dubai", "country": "United Arab Emirates", "region": "Middle East", "active_properties": 1, "total_beds": 14, "occupancy_rate_pct": Decimal("92.80"), "monthly_revenue_eur": Decimal("22400.00"), "expansion_target_beds": 150, "growth_potential": "AGGRESSIVE"},
        ]
        for hub in hubs:
            ExpansionHubKPI.objects.update_or_create(
                city=hub["city"],
                defaults=hub
            )

        self.stdout.write(self.style.SUCCESS("ILA Global Real Estate & Co-Living database successfully seeded!"))
