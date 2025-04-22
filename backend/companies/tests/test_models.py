# backend/companies/tests/test_models.py
from django.test import TestCase
from .models import Company

class CompanyModelTest(TestCase):
    def test_company_creation(self):
        company = Company.objects.create(
            name="Test Şirket",
            sector="Teknoloji",
            subscription_end="2025-12-31"
        )
        self.assertEqual(str(company), "Test Şirket")