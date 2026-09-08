import datetime
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import (
    Landlord,
    MasterLease,
    Property,
    Room,
    TenantUser,
    DutyRosterTask,
    SupplyProduct,
    ERPInvoice,
)


class GlobalRealEstateApiTests(APITestCase):
    def setUp(self):
        self.landlord = Landlord.objects.create(
            full_name="Braun Test",
            email="braun@test.de",
            country="Germany"
        )

        self.lease = MasterLease.objects.create(
            landlord=self.landlord,
            landlord_name="Braun Test",
            landlord_email="braun@test.de",
            landlord_phone="+49 69 1111",
            building_name="Skyline Test Hub",
            city_code="FFM",
            city_name="Frankfurt",
            country="Germany",
            address="Mainzer Landstr. 10",
            total_floors=4,
            total_capacity=10,
            monthly_master_rent=Decimal("5000.00"),
            currency="EUR",
            lease_start_date=datetime.date(2025, 1, 1),
            lease_end_date=datetime.date(2028, 1, 1),
            generated_property_uid="GLB-FFM-TEST1"
        )

        self.prop = Property.objects.create(
            master_lease=self.lease,
            property_uid="GLB-FFM-TEST1",
            title="Skyline Test Hub",
            city="Frankfurt",
            city_code="FFM",
            country="Germany",
            address="Mainzer Landstr. 10",
            image_url="https://example.com/img.jpg",
            total_rooms=10,
            total_valuation=Decimal("1000000.00"),
        )

        self.room = Room.objects.create(
            property=self.prop,
            room_uid="GLB-FFM-TEST1-RM1",
            room_number="101",
            room_type="Private Ensuite",
            sqm=Decimal("20.00"),
            regular_rent_amount=Decimal("450.00"),
            micro_investor_rent_amount=Decimal("330.00"),
            security_deposit_amount=Decimal("450.00"),
            currency="EUR",
            floor=1
        )

        self.tenant = TenantUser.objects.create(
            full_name="Marcus Vance Test",
            email="marcus@test.com",
            phone="+49 176 1111",
            role="MICRO_INVESTOR",
            option_type="OPTION_B",
            assigned_property=self.prop,
            assigned_room=self.room,
            assigned_room_uid="GLB-FFM-TEST1-RM1",
            property_title="Skyline Test Hub",
            city="Frankfurt",
            lease_start_date=datetime.date(2025, 1, 1),
            lease_end_date=datetime.date(2026, 1, 1),
            monthly_rent_charged=Decimal("330.00"),
            deposit_held=Decimal("450.00"),
            wallet_balance=Decimal("1000.00"),
            referral_code="REF-TEST-99"
        )

        self.task = DutyRosterTask.objects.create(
            property=self.prop,
            property_title="Skyline Test Hub",
            tenant=self.tenant,
            tenant_name=self.tenant.full_name,
            assigned_zone="Kitchen",
            scheduled_date=datetime.date.today(),
            day_of_week="Monday",
            status="PENDING"
        )

        self.supply = SupplyProduct.objects.create(
            sku="ILA-TEST-SKU",
            name="Test Towels",
            category="Linens",
            unit_price=Decimal("15.00"),
            in_stock=10
        )

    def test_health_check(self):
        url = reverse('global-studio-health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['service'], 'ila-global-proptech-drf')

    def test_properties_list(self):
        url = reverse('property-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_tenant_me(self):
        url = reverse('tenant-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Marcus Vance Test')
        self.assertEqual(response.data['referral_code'], 'REF-TEST-99')

    def test_tenant_update_option(self):
        url = reverse('tenant-update-option')
        response = self.client.post(url, {'option_type': 'OPTION_A'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['option_type'], 'OPTION_A')
        self.assertEqual(float(response.data['monthly_rent_charged']), 450.00)

    def test_duty_roster_reject_penalty(self):
        url = reverse('duty-roster-reject', kwargs={'pk': self.task.id})
        response = self.client.post(url, {'reviewer_name': 'Tester', 'reason': 'Dirty sink'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task']['status'], 'REJECTED_PENALIZED')
        self.assertEqual(float(response.data['penalty']['penalty_amount']), 35.00)
        self.tenant.refresh_from_db()
        self.assertEqual(float(self.tenant.deposit_held), 415.00)

    def test_supply_restock(self):
        url = reverse('supply-product-restock', kwargs={'sku': self.supply.sku})
        response = self.client.post(url, {'quantity': 25}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.in_stock, 35)
