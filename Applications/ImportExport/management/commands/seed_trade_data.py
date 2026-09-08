import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from Applications.ImportExport.models import (
    Importer,
    Exporter,
    RFQ,
    RFQProposal,
    Transaction,
    SmartVault,
    VaultSignature,
    AisTelemetry,
    ConsignmentDocument,
    CeoApproval,
    SanctionsLog,
    StaffMember,
    JobVacancy,
    LedgerEntry,
    TreasuryReserve,
    StrategicTieup,
    Article,
    DemandItem,
)


class Command(BaseCommand):
    help = 'Seeds initial reference datasets and verified seed entities for NEXUS B2B Platform'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding NEXUS B2B Trade & Treasury database...")

        # ----------------------------------------------------------------------
        # 1. Seed Treasury Reserves
        # ----------------------------------------------------------------------
        reserves = [
            {
                'currency': 'USD',
                'name': 'US Dollar Multi-Sig Reserves',
                'balance_formatted': '$28.40M USD',
                'balance_usd': Decimal('28400000.00'),
                'share_percent': '48.5%',
                'bank': 'JPMorgan Chase Tier 1',
                'tier': 'Primary Vault (AAA Bank)',
            },
            {
                'currency': 'EUR',
                'name': 'Euro Clearing & Single Market Pool',
                'balance_formatted': '€14.50M EUR',
                'balance_usd': Decimal('15800000.00'),
                'share_percent': '26.8%',
                'bank': 'Deutsche Bank Frankfurt',
                'tier': 'EU Central Clearing',
            },
            {
                'currency': 'SGD',
                'name': 'Singapore Dollar APAC Settlement Vault',
                'balance_formatted': 'S$12.20M SGD',
                'balance_usd': Decimal('9100000.00'),
                'share_percent': '15.5%',
                'bank': 'DBS Bank Singapore',
                'tier': 'APAC Clearing Node',
            },
            {
                'currency': 'USDC',
                'name': 'Digital Stablecoin Instant Escrow Vault',
                'balance_formatted': '$5.50M USDC',
                'balance_usd': Decimal('5500000.00'),
                'share_percent': '9.2%',
                'bank': 'Circle Institutional Custody',
                'tier': 'Smart Contract Pool',
            },
        ]
        for r in reserves:
            TreasuryReserve.objects.update_or_create(
                currency=r['currency'],
                defaults=r
            )

        # ----------------------------------------------------------------------
        # 2. Seed Verified Importers
        # ----------------------------------------------------------------------
        imp1, _ = Importer.objects.update_or_create(
            reference_id='IMP-1048',
            defaults={
                'name': 'Nordic Agro-Logistics AB',
                'country': 'Sweden',
                'flag': '🇸🇪',
                'tier': 'Verified Gold',
                'rating': '4.9 ★',
                'annual_volume_usd': Decimal('48500000.00'),
                'port_of_destination': 'Port of Gothenburg',
                'categories': ['Grains & Cereals', 'Specialty Feed', 'Bio-Fertilizers'],
                'contact_person': 'Elin Lindqvist (VP Procurement)',
                'contact_email': 'e.lindqvist@nordicagro.se',
                'credit_score': 'AAA (D&B 98/100)',
                'bank_partner': 'Nordea Trade Finance',
                'escrow_deposit_capacity_usd': Decimal('15000000.00'),
                'preferred_incoterms': ['CIF Gothenburg', 'DDP Malmo'],
                'historical_trades_count': 142
            }
        )

        imp2, _ = Importer.objects.update_or_create(
            reference_id='IMP-2091',
            defaults={
                'name': 'Apex Pacific Electronics Pte',
                'country': 'Singapore',
                'flag': '🇸🇬',
                'tier': 'Verified Gold',
                'rating': '5.0 ★',
                'annual_volume_usd': Decimal('120000000.00'),
                'port_of_destination': 'Port of Singapore',
                'categories': ['Semiconductors', 'Precision Sensors', 'Optical Cables'],
                'contact_person': 'Tan Wei Ming (Head of Supply)',
                'contact_email': 'wm.tan@apexpacific.sg',
                'credit_score': 'AAA (Standard & Poor Prime)',
                'bank_partner': 'DBS Treasury Services',
                'escrow_deposit_capacity_usd': Decimal('40000000.00'),
                'preferred_incoterms': ['FOB Hamburg', 'CIF Singapore'],
                'historical_trades_count': 288
            }
        )

        imp3, _ = Importer.objects.update_or_create(
            reference_id='IMP-3015',
            defaults={
                'name': 'Bavaria Heavy Machinery GmbH',
                'country': 'Germany',
                'flag': '🇩🇪',
                'tier': 'Verified Silver',
                'rating': '4.8 ★',
                'annual_volume_usd': Decimal('76000000.00'),
                'port_of_destination': 'Port of Hamburg',
                'categories': ['Hydraulic Components', 'Titanium Alloys', 'CNC Tooling'],
                'contact_person': 'Maximilian Weber (Chief Buyer)',
                'contact_email': 'weber@bavaria-heavy.de',
                'credit_score': 'AA+ (Creditreform Clean)',
                'bank_partner': 'Commerzbank Frankfurt',
                'escrow_deposit_capacity_usd': Decimal('22000000.00'),
                'preferred_incoterms': ['DDP Munich', 'CIF Hamburg'],
                'historical_trades_count': 94
            }
        )

        # ----------------------------------------------------------------------
        # 3. Seed Certified Exporters
        # ----------------------------------------------------------------------
        exp1, _ = Exporter.objects.update_or_create(
            reference_id='EXP-801',
            defaults={
                'name': 'Bavaria Semiconductor AG',
                'country': 'Germany',
                'flag': '🇩🇪',
                'tier': 'Certified Producer (Tier-1)',
                'rating': '5.0 ★',
                'annual_export_capacity_usd': Decimal('180000000.00'),
                'port_of_origin': 'Port of Hamburg',
                'specialties': ['Silicon Carbide Wafers', 'Industrial IGBT Modules', 'Automotive Sensors'],
                'compliance_certificates': ['ISO 9001:2015', 'IATF 16949', 'RoHS / REACH Certified', 'CE Mark'],
                'production_lead_time': '15 - 20 Days',
                'moq': '500 Wafers / 5,000 Modules',
                'contact_person': 'Dr. Stefan Meyer',
                'contact_email': 's.meyer@bavaria-semi.de',
                'bank_partner': 'Deutsche Bank AG',
                'inspection_agency': 'TÜV Süd Global Oracle',
                'factory_area_sqm': '85,000 m²',
                'established_year': 1998,
                'historical_exports_count': 412
            }
        )

        exp2, _ = Exporter.objects.update_or_create(
            reference_id='EXP-940',
            defaults={
                'name': 'Rhine Precision Metals KG',
                'country': 'Germany',
                'flag': '🇩🇪',
                'tier': 'Certified Producer (Tier-1)',
                'rating': '4.9 ★',
                'annual_export_capacity_usd': Decimal('95000000.00'),
                'port_of_origin': 'Port of Rotterdam',
                'specialties': ['Aero-grade Titanium Billets', 'Specialty Stainless Rods', 'Rolled Coils'],
                'compliance_certificates': ['ISO 14001', 'EN 9100 Aerospace', 'TÜV Rheinland Inspected'],
                'production_lead_time': '20 - 30 Days',
                'moq': '25 Metric Tons',
                'contact_person': 'Anke Richter',
                'contact_email': 'richter@rhine-metals.de',
                'bank_partner': 'LBBW Stuttgart',
                'inspection_agency': 'SGS International',
                'factory_area_sqm': '60,000 m²',
                'established_year': 2004,
                'historical_exports_count': 230
            }
        )

        # ----------------------------------------------------------------------
        # 4. Seed RFQs & Proposals
        # ----------------------------------------------------------------------
        rfq1, _ = RFQ.objects.update_or_create(
            reference_id='RFQ-881',
            defaults={
                'buyer': imp1,
                'title': 'High-Protein Grain Feed & Non-GMO Wheat Consignment',
                'hs_code': '1001.99.00',
                'target_quantity': '12,000 Metric Tons',
                'target_budget_usd': Decimal('3800000.00'),
                'incoterm': 'CIF Gothenburg',
                'delivery_deadline': '40 Days from Escrow Lock',
                'inspection_agency': 'SGS International Oracle',
                'status': 'Open for Bidding'
            }
        )

        RFQProposal.objects.get_or_create(
            rfq=rfq1,
            bidder_name='Baltic Agri Export Consortium',
            defaults={
                'total_price_usd': Decimal('3650000.00'),
                'unit_price_usd': Decimal('304.16'),
                'delivery_window': '30 - 35 Days',
                'payment_terms': '100% Nexus Smart Escrow (Multi-Sig Vault)',
                'inspection_guarantee': 'SGS Pre-Shipment Certificate Guaranteed',
                'is_accepted': False
            }
        )

        rfq2, _ = RFQ.objects.update_or_create(
            reference_id='RFQ-904',
            defaults={
                'buyer': imp2,
                'title': 'Industrial IGBT Power Modules for High-Speed Rail Inverters',
                'hs_code': '8541.29.00',
                'target_quantity': '10,000 Units',
                'target_budget_usd': Decimal('2450000.00'),
                'incoterm': 'FOB Hamburg',
                'delivery_deadline': '25 Days',
                'inspection_agency': 'TÜV Rheinland Clean Inspection',
                'status': 'Awarded & Escrow Locked'
            }
        )

        RFQProposal.objects.get_or_create(
            rfq=rfq2,
            bidder_name='Bavaria Semiconductor AG',
            defaults={
                'total_price_usd': Decimal('2400000.00'),
                'unit_price_usd': Decimal('240.00'),
                'delivery_window': '20 Days',
                'payment_terms': '100% Nexus 3-of-4 Smart Escrow',
                'inspection_guarantee': 'TÜV Pre-Shipment Inspection Included',
                'is_accepted': True
            }
        )

        # ----------------------------------------------------------------------
        # 5. Seed Consignment Transactions & Escrow Smart Vaults
        # ----------------------------------------------------------------------
        tx1, _ = Transaction.objects.update_or_create(
            reference_id='TX-74820',
            defaults={
                'title': 'Automotive IGBT Power Modules (10,000 Pcs)',
                'buyer': 'Apex Pacific Electronics Pte',
                'buyer_flag': '🇸🇬',
                'seller': 'Bavaria Semiconductor AG',
                'seller_flag': '🇩🇪',
                'amount_usd': Decimal('2400000.00'),
                'escrow_status': '20% Released • Vessel in Deep-Sea Transit',
                'escrow_progress': 50,
                'stage_index': 3,
                'bill_of_lading': 'BL-MAEU-98217462',
                'shipping_line': 'Maersk Line / CMA CGM Consortium',
                'port_of_loading': 'Port of Hamburg (DE)',
                'port_of_discharge': 'Port of Singapore (SG)',
                'current_stage': 'Stage 3: Deep-Sea Maritime Transit & AIS Voyage Tracking',
                'eta': '14 Days (En Route to Suez Canal)',
                'status_badge': 'At Sea',
                'last_update': 'Vessel passed English Channel waypoint. SGS inspection certificate hash confirmed on smart vault.',
                'container_count': 2,
                'container_type': '40ft High Cube Temperature-Controlled Reefer',
                'hs_code': '8541.29.00',
                'incoterm': 'CIF Singapore'
            }
        )

        vault1, _ = SmartVault.objects.update_or_create(
            transaction=tx1,
            defaults={
                'contract_address': '0x8fB2A91D3C49B55e09f7a771D22D16C4b80e889F',
                'multi_sig_requirement': '3 of 4 Signatures Required',
                'collateral_rating': 'AAA Backed by Bank Tier 1',
                'funds_locked_usd': Decimal('2400000.00'),
                'funds_released_usd': Decimal('480000.00')
            }
        )

        # 4 Signatures for 3-of-4 Multi-Sig
        signatures = [
            {'role': 'Buyer Signatory', 'signer_name': 'Tan Wei Ming (Apex Pacific)', 'signed': True, 'timestamp': '2026-03-01 10:14 UTC'},
            {'role': 'Seller Signatory', 'signer_name': 'Dr. Stefan Meyer (Bavaria Semi)', 'signed': True, 'timestamp': '2026-03-01 11:30 UTC'},
            {'role': 'SGS Inspection Oracle', 'signer_name': 'TÜV Rheinland Hamburg Node', 'signed': True, 'timestamp': '2026-03-03 16:45 UTC'},
            {'role': 'Nexus Neutral Trustee', 'signer_name': 'NEXUS Automated Custody Contract', 'signed': False, 'timestamp': 'Pending Stage 4 Clearance'},
        ]
        for s in signatures:
            VaultSignature.objects.update_or_create(
                vault=vault1,
                role=s['role'],
                defaults=s
            )

        AisTelemetry.objects.update_or_create(
            transaction=tx1,
            defaults={
                'vessel_name': 'CMA CGM Palais Royal',
                'coordinates': '36.1408° N, 5.3536° W (Strait of Gibraltar)',
                'current_speed_knots': '18.4 Knots',
                'heading': '108° (East-South-East)',
                'nautical_miles_covered': '1,840 NM / 7,420 NM',
                'next_waypoint': 'Port Said / Suez Canal Approach'
            }
        )

        docs = [
            {'doc_type': 'Pro-Forma Bill of Lading', 'name': 'BL-MAEU-98217462-Verified.pdf', 'file_url': 'https://nexus.trade/docs/bl-98217462.pdf', 'status': 'Verified by Maersk', 'size': '1.2 MB'},
            {'doc_type': 'SGS Inspection Certificate', 'name': 'SGS-DE-Q3-88219.pdf', 'file_url': 'https://nexus.trade/docs/sgs-88219.pdf', 'status': 'Cryptographically Signed', 'size': '3.4 MB'},
            {'doc_type': 'Commercial Invoice', 'name': 'INV-BAV-2026-1049.pdf', 'file_url': 'https://nexus.trade/docs/inv-1049.pdf', 'status': 'Escrow Locked', 'size': '450 KB'},
        ]
        for d in docs:
            ConsignmentDocument.objects.update_or_create(
                transaction=tx1,
                name=d['name'],
                defaults=d
            )

        # ----------------------------------------------------------------------
        # 6. Seed CEO Approvals Desk
        # ----------------------------------------------------------------------
        approvals = [
            {
                'reference_id': 'APP-901',
                'title': 'High-Capacity Semiconductor Escrow Release ($2.40M)',
                'buyer': 'Apex Pacific Electronics Pte',
                'seller': 'Bavaria Semiconductor AG',
                'value_usd': Decimal('2400000.00'),
                'department': 'Trade Finance & Escrow Treasury',
                'risk_score': 'Low (1.2/10)',
                'urgent': True,
                'memo': 'TÜV inspection confirmed 100% yield with zero defect rate. Milestone 2 release verified by automated oracle.',
                'status': 'Pending Authorization'
            },
            {
                'reference_id': 'APP-902',
                'title': 'Grain Cargo Marine Insurance Underwrite ($3.80M)',
                'buyer': 'Nordic Agro-Logistics AB',
                'seller': 'Baltic Agri Export Consortium',
                'value_usd': Decimal('3800000.00'),
                'department': 'Risk & Underwriting',
                'risk_score': 'Medium (2.4/10)',
                'urgent': False,
                'memo': 'Vessel age 6 years, Lloyd’s 1A certified. Escrow deposit capacity confirmed by Nordea Bank.',
                'status': 'Pending Authorization'
            },
        ]
        for a in approvals:
            CeoApproval.objects.update_or_create(
                reference_id=a['reference_id'],
                defaults=a
            )

        # ----------------------------------------------------------------------
        # 7. Seed Sanctions & Compliance Radar
        # ----------------------------------------------------------------------
        sanctions = [
            {
                'reference_id': 'SANC-4821',
                'entity_name': 'Nordic Agro-Logistics AB',
                'country': 'Sweden',
                'flag': '🇸🇪',
                'entity_type': 'Screened Importer',
                'watchlists_checked': ['OFAC SDN', 'EU Consolidated', 'UN Sanctions', 'FATF Clean'],
                'risk_score': '0.1 / 10 (Clean)',
                'status': 'Cleared & Whitelisted',
                'certificate_hash': '0x9a8f21bc08419dc81e813f281e09bc8411fa0e18',
            },
            {
                'reference_id': 'SANC-4822',
                'entity_name': 'Bavaria Semiconductor AG',
                'country': 'Germany',
                'flag': '🇩🇪',
                'entity_type': 'Certified Producer',
                'watchlists_checked': ['OFAC SDN', 'EU Consolidated', 'German BAFA Export Control', 'UN Sanctions'],
                'risk_score': '0.0 / 10 (Immaculate)',
                'status': 'Cleared & Whitelisted',
                'certificate_hash': '0x7e849fa189c204918e99bc1829381749fa918239',
            },
            {
                'reference_id': 'SANC-4823',
                'entity_name': 'Apex Pacific Electronics Pte',
                'country': 'Singapore',
                'flag': '🇸🇬',
                'entity_type': 'Screened Buyer',
                'watchlists_checked': ['OFAC SDN', 'MAS Singapore Watchlist', 'UN Sanctions', 'EU Consolidated'],
                'risk_score': '0.2 / 10 (Clean)',
                'status': 'Cleared & Whitelisted',
                'certificate_hash': '0x5c9081e819fa00bc1928418f78a91048bcae9124',
            },
        ]
        for s in sanctions:
            SanctionsLog.objects.update_or_create(
                reference_id=s['reference_id'],
                defaults=s
            )

        # ----------------------------------------------------------------------
        # 8. Seed HR Staff & Vacancies
        # ----------------------------------------------------------------------
        staff = [
            {
                'employee_id': 'EMP-101',
                'name': 'Alexander von Hessel',
                'role': 'Director of Trade Operations & Escrow Custody',
                'department': 'Global Trade Operations',
                'location': 'Frankfurt, Germany',
                'timezone': 'UTC+1',
                'email': 'a.hessel@nexus.trade',
                'clearance_level': 'Level 4 (Executive Multi-Sig)',
                'base_salary_usd': Decimal('185000.00'),
                'monthly_commission_usd': Decimal('14500.00'),
                'active_caseload': 14,
                'performance_rating': '99.4%',
                'status': 'On Duty (Active)',
                'avatar_bg': 'bg-emerald-500/20 text-emerald-400'
            },
            {
                'employee_id': 'EMP-102',
                'name': 'Mei Ling Tan',
                'role': 'Senior Maritime Telemetry & Port Oracle Specialist',
                'department': 'Logistics & AIS Telemetry',
                'location': 'Singapore',
                'timezone': 'UTC+8',
                'email': 'ml.tan@nexus.trade',
                'clearance_level': 'Level 3 (Port Oracle Signatory)',
                'base_salary_usd': Decimal('140000.00'),
                'monthly_commission_usd': Decimal('8500.00'),
                'active_caseload': 22,
                'performance_rating': '97.8%',
                'status': 'On Duty (Active)',
                'avatar_bg': 'bg-teal-500/20 text-teal-400'
            },
        ]
        for st in staff:
            StaffMember.objects.update_or_create(
                employee_id=st['employee_id'],
                defaults=st
            )

        JobVacancy.objects.update_or_create(
            reference_id='VAC-12',
            defaults={
                'title': 'Senior Maritime Compliance Counsel',
                'department': 'Legal & Sanctions Radar',
                'location': 'Frankfurt / Remote',
                'job_type': 'Full-Time',
                'applicants_count': 18,
                'urgency': 'High Priority',
                'salary_range': '$140,000 - $175,000'
            }
        )

        # ----------------------------------------------------------------------
        # 9. Seed Treasury Ledger Entries
        # ----------------------------------------------------------------------
        ledger = [
            {
                'reference_id': 'LED-9101',
                'tx_ref': 'TX-74820',
                'description': '100% Escrow Collateral Lock for Automotive IGBT Shipment',
                'entry_type': 'Deposit (Credit)',
                'category': 'Smart Escrow Vault Funding',
                'amount_usd': Decimal('2400000.00'),
                'fee_earned_usd': Decimal('24000.00'),
                'status': 'Confirmed On-Chain',
                'ledger_hash': '0x1a8f90281bca0918e901fbc8192081e81fa09823',
            },
            {
                'reference_id': 'LED-9102',
                'tx_ref': 'TX-74820',
                'description': 'Stage 2 Milestone Disbursement (20%) upon SGS Pre-Shipment Pass',
                'entry_type': 'Disbursement (Debit)',
                'category': 'Supplier Milestone Payout',
                'amount_usd': Decimal('480000.00'),
                'fee_earned_usd': Decimal('0.00'),
                'status': 'Executed via SEPA Instant',
                'ledger_hash': '0x88fc910a8271e8910fbca8192048bcae91823901',
            }
        ]
        for l in ledger:
            LedgerEntry.objects.update_or_create(
                reference_id=l['reference_id'],
                defaults=l
            )

        # ----------------------------------------------------------------------
        # 10. Seed Strategic Tie-ups
        # ----------------------------------------------------------------------
        StrategicTieup.objects.update_or_create(
            reference_id='MOU-501',
            defaults={
                'partner_name': 'Port of Gothenburg Logistics Authority',
                'partner_type': 'Port Authority Node',
                'country': 'Sweden',
                'flag': '🇸🇪',
                'scope': 'Automated customs telemetry ingestion, priority green-lane discharge, and AIS berth telemetry integration.',
                'signed_date': '2025-11-14',
                'status': 'Active Operational Partnership',
                'mou_document_url': 'https://nexus.trade/mou/gothenburg-nexus.pdf'
            }
        )

        StrategicTieup.objects.update_or_create(
            reference_id='MOU-502',
            defaults={
                'partner_name': 'SGS International Global Oracle Network',
                'partner_type': 'Inspection Agency',
                'country': 'Switzerland',
                'flag': '🇨🇭',
                'scope': 'Cryptographic digital pre-shipment inspection verification oracle on smart contracts with zero human delay.',
                'signed_date': '2025-08-20',
                'status': 'Active Operational Partnership',
                'mou_document_url': 'https://nexus.trade/mou/sgs-nexus-oracle.pdf'
            }
        )

        # ----------------------------------------------------------------------
        # 11. Seed Articles & Demands
        # ----------------------------------------------------------------------
        Article.objects.update_or_create(
            slug='red-sea-maritime-corridor-intelligence-q3',
            defaults={
                'title': 'Red Sea & Cape of Good Hope Routing Economics: Q3 Strategic Analysis',
                'summary': 'Analysis of transit times, bunker fuel surcharges, and smart escrow milestone adjustments for maritime trade between Europe and APAC.',
                'content': (
                    'Container freight rates and transit durations continue to reflect cape routing premiums. '
                    'With average vessel speeds maintained at 18.5 knots, smart contract milestone triggers '
                    'ensure capital liquidity remains predictable through multi-sig escrow consensus.'
                ),
                'category': 'Maritime Intelligence',
                'author': 'Alexander von Hessel',
                'read_time': '6 min read',
                'is_featured': True
            }
        )

        DemandItem.objects.update_or_create(
            title='Industrial Grade Silicon Carbide Wafers (150mm & 200mm)',
            defaults={
                'hs_code': '2849.20.00',
                'origin_country': 'Germany / Japan',
                'destination_country': 'Singapore',
                'volume': '25,000 Wafers',
                'urgency': 'High Urgency (Q3 Production)',
                'budget_usd': Decimal('6250000.00'),
                'status': 'Sourcing Active'
            }
        )

        self.stdout.write(self.style.SUCCESS("NEXUS B2B Trade & Logistics database successfully seeded!"))
