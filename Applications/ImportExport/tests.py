from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import (
    Transaction,
    ConsignmentStage,
    SmartVault,
    VaultSignature,
    CeoApproval,
    SanctionsLog,
    Importer,
    RFQ,
    StrategicTieup,
    StaffMember,
    PlatformSettings,
)


class NexusApiTests(APITestCase):
    def setUp(self):
        self.importer = Importer.objects.create(
            reference_id='IMP-TEST-01',
            name='Bavaria Agri-Grain Import GmbH',
            country='Germany',
            port_of_destination='Port of Hamburg',
            contact_person='Dr. Klaus Lindner',
            contact_email='klaus@bavaria-agri.de',
            bank_partner='Deutsche Bank AG Frankfurt'
        )

        self.rfq = RFQ.objects.create(
            reference_id='RFQ-TEST-881',
            buyer=self.importer,
            title='50,000 MT Milling Wheat',
            hs_code='1001.99.00',
            target_quantity='50,000 MT',
            target_budget_usd=Decimal('14200000.00'),
            incoterm='CIF Hamburg',
            delivery_deadline='Nov 30, 2026',
            inspection_agency='SGS International Geneva'
        )

        self.tx = Transaction.objects.create(
            reference_id='TX-TEST-01',
            title='Industrial Steel Shipment',
            buyer='Apex Tech Ltd',
            seller='Bavaria Semi AG',
            amount_usd=Decimal('2500000.00'),
            escrow_status='100% Escrow Funded',
            stage_index=ConsignmentStage.STAGE_1,
            bill_of_lading='BL-TEST-12345',
            port_of_loading='Hamburg',
            port_of_discharge='Rotterdam',
            current_stage='Stage 1: Contract Signed',
            eta='20 Days',
            hs_code='7209.16.00'
        )

        self.vault = SmartVault.objects.create(
            transaction=self.tx,
            contract_address='0xTEST981240182401824012841209410294102941',
            multi_sig_requirement='3 of 4 Signatures Required',
            collateral_rating='AAA Backed by Bank Tier 1',
            funds_locked_usd=Decimal('2500000.00'),
            funds_released_usd=Decimal('0.00')
        )

        self.sig_ceo = VaultSignature.objects.create(
            vault=self.vault,
            role='CEO Multi-Sig Signatory',
            signer_name='CEO Keyholder',
            signed=False,
            timestamp='Pending'
        )

        self.approval = CeoApproval.objects.create(
            reference_id='APP-TEST-99',
            title='Test Deal Authorization',
            buyer='Apex Tech',
            seller='Bavaria Semi',
            value_usd=Decimal('2500000.00'),
            status='Pending Authorization'
        )

        self.tieup = StrategicTieup.objects.create(
            reference_id='MOU-TEST-01',
            partnership_title='Baltic-Mediterranean Trade Corridor',
            lead_party='Nordic Agro-Logistics',
            counter_party='Valencia Ceramic SL',
            current_stage='Initial Due Diligence Review',
            sla_compliance='99.1%'
        )

        self.staff = StaffMember.objects.create(
            employee_id='EMP-TEST-01',
            name='Elena Rostova',
            role='Trade Finance Broker',
            department='Trade Brokers',
            location='Singapore Hub',
            timezone='SGT (GMT+8)',
            email='e.rostova@nexus-trade.com',
            clearance_level='Level 3',
            base_salary_usd=Decimal('140000.00'),
            status='Active Officer'
        )

    def test_advance_escrow_milestone(self):
        url = reverse('transactions-advance-milestone', kwargs={'pk': self.tx.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stageIndex'], 2)
        self.assertEqual(response.data['statusBadge'], 'Loading Passed')

    def test_sign_vault(self):
        url = reverse('transactions-sign-vault', kwargs={'pk': self.tx.id})
        response = self.client.post(url, {'signerRole': 'CEO'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sig_ceo.refresh_from_db()
        self.assertTrue(self.sig_ceo.signed)

    def test_sanctions_instant_screening(self):
        url = reverse('compliance-sanctions-screen-entity')
        payload = {'entityName': 'Global Baltic Traders Ltd', 'country': 'Estonia'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Cleared & Whitelisted')
        self.assertTrue(response.data['certificateHash'].startswith('0x'))

    def test_ceo_bulk_approve(self):
        url = reverse('ceo-approvals-bulk-approve')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.approval.refresh_from_db()
        self.assertEqual(self.approval.status, 'Authorized')

    def test_portal_metrics(self):
        url = reverse('portal-metrics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalVolume', response.data)
        self.assertIn('totalTradeVolumeUsd', response.data)
        self.assertIn('activeTrades', response.data)

    def test_accept_proposal(self):
        url = reverse('rfqs-accept-proposal', kwargs={'pk': self.rfq.id})
        payload = {
            'proposal': {
                'id': 'PROP-301',
                'bidderName': 'Odessa Agrarian Grain Terminals',
                'totalPriceUsd': 13900000,
                'deliveryWindow': '22 Days'
            }
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'awarded')
        self.assertEqual(response.data['rfqId'], self.rfq.reference_id)
        self.assertIn('transactionId', response.data)

    def test_tieup_advance_milestone(self):
        url = reverse('tieups-advance-milestone', kwargs={'pk': self.tieup.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['currentStage'], 'Executive Board Approval & Final Signing')
        self.assertEqual(response.data['slaCompliance'], '100%')

    def test_payroll_disburse(self):
        url = reverse('hr-staff-payroll-disburse')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'disbursed')
        self.assertGreaterEqual(response.data['staffCount'], 1)

    def test_governance_settings(self):
        url = reverse('governance-settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('escrowFeePercent', response.data)

        patch_resp = self.client.patch(url, {'escrowFeePercent': '2.50'}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data['escrowFeePercent'], '2.50')
