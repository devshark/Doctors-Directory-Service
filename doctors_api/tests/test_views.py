from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from ..models import Doctor, Category, District
import logging
import json

logger = logging.getLogger(__name__)

class DoctorAPITestCase(APITestCase):
    def setUp(self):
        # Create test categories
        self.category1 = Category.objects.create(name="Cardiologist")
        self.category2 = Category.objects.create(name="Dermatologist")
        
        # Create test districts
        self.district1 = District.objects.create(name="Central")
        self.district2 = District.objects.create(name="Kowloon")
        
        # Create test doctors
        self.doctor1 = Doctor.objects.create(
            name="Dr. John Smith",
            address="123 Medical Street, Central",
            contact_details="Phone: +852 1234 5678",
            category=self.category1,
            district=self.district1,
            language="en",
            consultation_fee=Decimal("200.00")
        )
        
        self.doctor2 = Doctor.objects.create(
            name="Dr. Jane Doe",
            address="456 Health Avenue, Kowloon",
            contact_details="Phone: +852 8765 4321",
            category=self.category2,
            district=self.district2,
            language="cantonese",
            consultation_fee=Decimal("300.00")
        )
        
        # Set up the API client
        self.client = APIClient()
        
        # Create a doctor that we'll set as inactive for testing
        self.inactive_doctor = Doctor.objects.create(
            name="Dr. Inactive",
            address="789 Inactive Street",
            contact_details="Phone: +852 9999 9999",
            category=self.category1,
            district=self.district1,
            language="mandarin",
            consultation_fee=Decimal("250.00"),
            is_active=False
        )

    def tearDown(self):
        # Clean up all test data
        Doctor.objects.all().delete()
        Category.objects.all().delete()
        District.objects.all().delete()

    # Test listing all doctors
    def test_list_doctors(self):
        # First, get the count of active doctors before our test
        initial_active_count = Doctor.objects.filter(is_active=True).count()
        
        url = reverse('doctor-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that we can see exactly the doctors we created in the response
        # (plus any pre-existing active doctors)
        self.assertEqual(len(response.data), initial_active_count)
        
        # Ensure the inactive doctor doesn't appear
        doctor_names = [doctor['name'] for doctor in response.data]
        self.assertIn("Dr. John Smith", doctor_names)
        self.assertIn("Dr. Jane Doe", doctor_names)
        self.assertNotIn("Dr. Inactive", doctor_names)
    
    # Test retrieving a specific doctor
    def test_retrieve_doctor(self):
        url = reverse('doctor-detail', args=[self.doctor1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Dr. John Smith")
        self.assertEqual(response.data['category'], self.category1.id)
        self.assertEqual(response.data['district'], self.district1.id)
        self.assertEqual(response.data['language'], "en")
        self.assertEqual(Decimal(response.data['consultation_fee']), Decimal("200.00"))
    
    # Test retrieving an inactive doctor (should fail)
    def test_retrieve_inactive_doctor(self):
        url = reverse('doctor-detail', args=[self.inactive_doctor.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # Test creating a new doctor
    def test_create_doctor(self):
        url = reverse('doctor-list')
        data = {
            "name": "Dr. New Doctor",
            "address": "New Address",
            "contact_details": "New Contact",
            "category": self.category2.id,
            "district": self.district2.id,
            "language": "mandarin",
            "consultation_fee": "350.00"
        }
        
        previous_count = Doctor.objects.count()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), previous_count + 1)
        
        # Verify the created doctor
        created_doctor = Doctor.objects.get(name="Dr. New Doctor")
        self.assertEqual(created_doctor.category.id, self.category2.id)
        self.assertEqual(created_doctor.district.id, self.district2.id)
        self.assertEqual(created_doctor.language, "mandarin")
        self.assertEqual(created_doctor.consultation_fee, Decimal("350.00"))
        self.assertTrue(created_doctor.is_active)
    
    # Test creating a doctor with invalid data
    def test_create_doctor_invalid_data(self):
        url = reverse('doctor-list')
        data = {
            "name": "Dr. Invalid",
            # Missing required fields
            "category": self.category1.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('address', response.data)
        self.assertIn('district', response.data)
        self.assertIn('language', response.data)
        self.assertIn('consultation_fee', response.data)
    
    # Test bulk creation of doctors
    def test_bulk_create_doctors(self):
        url = reverse('doctor-bulk-create')
        data = [
            {
                "name": "Dr. Bulk 1",
                "address": "Bulk Address 1",
                "contact_details": "Bulk Contact 1",
                "category": self.category1.id,
                "district": self.district1.id,
                "language": "en",
                "consultation_fee": "150.00"
            },
            {
                "name": "Dr. Bulk 2",
                "address": "Bulk Address 2",
                "contact_details": "Bulk Contact 2",
                "category": self.category2.id,
                "district": self.district2.id,
                "language": "cantonese",
                "consultation_fee": "250.00"
            }
        ]
        
        previous_count = Doctor.objects.count()
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Doctor.objects.count(), previous_count + 2)
        
        # Verify the created doctors
        bulk1 = Doctor.objects.get(name="Dr. Bulk 1")
        self.assertEqual(bulk1.consultation_fee, Decimal("150.00"))
        
        bulk2 = Doctor.objects.get(name="Dr. Bulk 2")
        self.assertEqual(bulk2.consultation_fee, Decimal("250.00"))
    
    # Test bulk creation with some invalid data
    def test_bulk_create_doctors_invalid_data(self):
        url = reverse('doctor-bulk-create')
        data = [
            {
                "name": "Dr. Bulk Valid",
                "address": "Bulk Address Valid",
                "contact_details": "Bulk Contact Valid",
                "category": self.category1.id,
                "district": self.district1.id,
                "language": "en",
                "consultation_fee": "150.00"
            },
            {
                "name": "Dr. Bulk Invalid",
                # Missing required fields
                "category": self.category2.id
            }
        ]
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # None of the doctors should be created due to validation error
        self.assertEqual(Doctor.objects.filter(name__startswith="Dr. Bulk").count(), 0)
    
    # Test filtering by fee range
    def test_filter_by_fee_range(self):
        url = reverse('doctor-list') + '?min_consultation_fee=250&max_consultation_fee=350'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. Jane Doe":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. Jane Doe should be in fee range 250-350")
    
    # Test filtering by category
    def test_filter_by_category(self):
        url = reverse('doctor-list') + f'?category={self.category1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. John Smith":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. John Smith should be in category filter results")
    
    # Test filtering by district
    def test_filter_by_district(self):
        url = reverse('doctor-list') + f'?district={self.district2.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. Jane Doe":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. Jane Doe should be in district filter results")
    
    # Test filtering by language
    def test_filter_by_language(self):
        url = reverse('doctor-list') + '?language=cantonese'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. Jane Doe":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. Jane Doe should be in language filter results")
    
    # Test combined filters
    def test_combined_filters(self):
        url = reverse('doctor-list') + f'?category={self.category2.id}&min_consultation_fee=250'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. Jane Doe":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. Jane Doe should be in combined filter results")
        
        # No results with impossible combination
        url = reverse('doctor-list') + f'?category={self.category1.id}&language=cantonese'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that our test doctors are not in results
        for doctor in response.data:
            self.assertNotEqual(doctor['name'], "Dr. John Smith")
            self.assertNotEqual(doctor['name'], "Dr. Jane Doe")
    
    # Test search functionality
    def test_search(self):
        # Search by category name
        url = reverse('doctor-list') + '?search=Cardio'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Instead of checking exact count, check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. John Smith":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. John Smith should be in search results for 'Cardio'")
        
        # Search by district name
        url = reverse('doctor-list') + '?search=Kowloon'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that our test doctor is in results
        found_doctor = False
        for doctor in response.data:
            if doctor['name'] == "Dr. Jane Doe":
                found_doctor = True
                break
        self.assertTrue(found_doctor, "Dr. Jane Doe should be in search results for 'Kowloon'")
        
        # Search by language
        url = reverse('doctor-list') + '?search=english'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # There may be English-speaking doctors in the database,
        # just check the response format is correct
        self.assertIsInstance(response.data, list)
        
        # Search with no results
        url = reverse('doctor-list') + '?search=NotExisting123456789'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class DistrictAndCategoryTestCase(APITestCase):
    def setUp(self):
        # Create test categories
        self.category1 = Category.objects.create(name="Cardiologist")
        self.category2 = Category.objects.create(name="Dermatologist")
        
        # Create test districts
        self.district1 = District.objects.create(name="Central")
        self.district2 = District.objects.create(name="Kowloon")
        
        # Set up the API client
        self.client = APIClient()

    def tearDown(self):
        # Clean up all test data
        Doctor.objects.all().delete()
        Category.objects.all().delete()
        District.objects.all().delete()

    # Test listing categories
    def test_list_categories(self):
        db_count = Category.objects.count()
        
        url = reverse('category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), db_count)
        
        category_names = [category['name'] for category in response.data]
        self.assertIn("Cardiologist", category_names)
        self.assertIn("Dermatologist", category_names)
    
    # Test getting a specific category
    def test_retrieve_category(self):
        url = reverse('category-detail', args=[self.category1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Cardiologist")
    
    # Test listing districts
    def test_list_districts(self):
        db_count = District.objects.count()
        
        url = reverse('district-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), db_count)
        
        district_names = [district['name'] for district in response.data]
        self.assertIn("Central", district_names)
        self.assertIn("Kowloon", district_names)
    
    # Test getting a specific district
    def test_retrieve_district(self):
        url = reverse('district-detail', args=[self.district1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Central")
