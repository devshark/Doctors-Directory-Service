from django.test import TestCase
from doctors_api.models import Doctor, Category, District
from decimal import Decimal
from django.utils import translation
from django.db import IntegrityError
from django.db.models import ProtectedError

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cardiologist")

    def test_category_creation(self):
        """Test Category model creation"""
        self.assertEqual(self.category.name, "Cardiologist")
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(str(self.category), "Cardiologist")

    def test_category_ordering(self):
        """Test Category model ordering"""
        Category.objects.create(name="Dermatologist")
        Category.objects.create(name="Allergist")
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Allergist")  # Alphabetical ordering
        self.assertEqual(categories[1].name, "Cardiologist")
        self.assertEqual(categories[2].name, "Dermatologist")


class DistrictModelTest(TestCase):
    def setUp(self):
        self.district = District.objects.create(name="Central")

    def test_district_creation(self):
        """Test District model creation"""
        self.assertEqual(self.district.name, "Central")
        self.assertTrue(isinstance(self.district, District))
        self.assertEqual(str(self.district), "Central")

    def test_district_ordering(self):
        """Test District model ordering"""
        District.objects.create(name="Kowloon")
        District.objects.create(name="Aberdeen")
        districts = District.objects.all()
        self.assertEqual(districts[0].name, "Aberdeen")  # Alphabetical ordering
        self.assertEqual(districts[1].name, "Central")
        self.assertEqual(districts[2].name, "Kowloon")


class DoctorModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cardiologist")
        self.district = District.objects.create(name="Central")
        self.doctor = Doctor.objects.create(
            name="Dr. John Smith",
            address="123 Medical Street, Central",
            contact_details="Phone: +852 1234 5678",
            category=self.category,
            district=self.district,
            language="en",
            consultation_fee=Decimal("200.00"),
            is_active=True
        )

    def test_doctor_creation(self):
        """Test Doctor model creation"""
        self.assertEqual(self.doctor.name, "Dr. John Smith")
        self.assertEqual(self.doctor.address, "123 Medical Street, Central")
        self.assertEqual(self.doctor.contact_details, "Phone: +852 1234 5678")
        self.assertEqual(self.doctor.category, self.category)
        self.assertEqual(self.doctor.district, self.district)
        self.assertEqual(self.doctor.language, "en")
        self.assertEqual(self.doctor.consultation_fee, Decimal("200.00"))
        self.assertTrue(self.doctor.is_active)
        self.assertEqual(str(self.doctor), "Dr. John Smith")

    def test_doctor_methods(self):
        """Test Doctor custom methods"""
        self.assertEqual(self.doctor.category_name(), "Cardiologist")
        self.assertEqual(self.doctor.district_name(), "Central")
        
        # Test with English as the active language
        with translation.override('en'):
            self.assertEqual(self.doctor.language_name(), "English")
        
        # Test with a different language
        self.doctor.language = "cantonese"
        self.doctor.save()
        with translation.override('en'):
            self.assertEqual(self.doctor.language_name(), "Cantonese")

        # Test with an unknown language code
        self.doctor.language = "unknown"
        self.doctor.save()
        with translation.override('en'):
            self.assertIsNone(self.doctor.language_name(), "Should return None for unknown language code")

    def test_doctor_soft_delete(self):
        """Test Doctor soft delete functionality"""
        # Initially doctor is active
        self.assertTrue(self.doctor.is_active)
        
        # After calling delete, doctor should be inactive but still exist
        self.doctor.delete()
        self.assertFalse(self.doctor.is_active)
        self.assertTrue(Doctor.objects.filter(pk=self.doctor.pk).exists())
        
        # After calling restore, doctor should be active again
        self.doctor.restore()
        self.assertTrue(self.doctor.is_active)

    def test_doctor_ordering(self):
        """Test Doctor model ordering"""
        Doctor.objects.create(
            name="Dr. Adam Brown",
            address="456 Health Avenue, Kowloon",
            contact_details="Phone: +852 8765 4321",
            category=self.category,
            district=self.district,
            language="mandarin",
            consultation_fee=Decimal("300.00")
        )
        Doctor.objects.create(
            name="Dr. Zoe Williams",
            address="789 Medical Road, Tsim Sha Tsui",
            contact_details="Phone: +852 2345 6789",
            category=self.category,
            district=self.district,
            language="cantonese",
            consultation_fee=Decimal("250.00")
        )
        
        doctors = Doctor.objects.all()
        self.assertEqual(doctors[0].name, "Dr. Adam Brown")  # Alphabetical ordering
        self.assertEqual(doctors[1].name, "Dr. John Smith")
        self.assertEqual(doctors[2].name, "Dr. Zoe Williams")

    def test_category_delete_protection(self):
        """Test that Category cannot be deleted when referenced by a Doctor"""
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_district_delete_protection(self):
        """Test that District cannot be deleted when referenced by a Doctor"""
        with self.assertRaises(ProtectedError):
            self.district.delete()

    def test_required_fields(self):
        """Test that required fields cannot be null"""
        with self.assertRaises(IntegrityError):
            Doctor.objects.create(
                name="Dr. Missing Fields",
                # Missing address
                contact_details="Phone: +852 9999 8888",
                # Missing category
                district=self.district,
                language="en",
                consultation_fee=Decimal("150.00")
            )

    def test_active_queryset(self):
        """Test the custom queryset method for active doctors"""
        # Create another active doctor and an inactive doctor
        active_doctor = Doctor.objects.create(
            name="Dr. Active",
            address="Active Street",
            contact_details="Phone: +852 1111 2222",
            category=self.category,
            district=self.district,
            language="en",
            consultation_fee=Decimal("100.00"),
            is_active=True
        )
        
        inactive_doctor = Doctor.objects.create(
            name="Dr. Inactive",
            address="Inactive Street",
            contact_details="Phone: +852 3333 4444",
            category=self.category,
            district=self.district,
            language="en",
            consultation_fee=Decimal("150.00"),
            is_active=False
        )
        
        # The queryset should only include active doctors
        active_doctors_count = Doctor.objects.filter(is_active=True).count()
        self.assertEqual(active_doctors_count, 2)  # Original + active_doctor
        
        # Make another doctor inactive
        active_doctor.delete()
        active_doctors_count = Doctor.objects.filter(is_active=True).count()
        self.assertEqual(active_doctors_count, 1)  # Original + inactive_doctor (which is still in DB)
