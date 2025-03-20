from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from doctors_api.models import Doctor, Category, District
from decimal import Decimal


class APIInternationalizationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.category = Category.objects.create(name="Cardiologist")
        self.district = District.objects.create(name="Central")
        self.doctor = Doctor.objects.create(
            name="Dr. John Smith",
            address="123 Medical Street, Central",
            contact_details="Phone: +852 1234 5678",
            category=self.category,
            district=self.district,
            language="en",
            consultation_fee=Decimal("200.00")
        )
    
    def tearDown(self):
        Doctor.objects.all().delete()
        Category.objects.all().delete()
        District.objects.all().delete()
    
    def test_delete_doctor_message_english(self):
        """Test the error message when deleting a doctor with English language header"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'], "Method \"DELETE\" not allowed.")
    
    def test_delete_doctor_message_zh_hant(self):
        """Test the error message when deleting a doctor with Traditional Chinese language header"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='zh-hant')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Check that the message is not the English version
        # This test assumes translations have been set up
        self.assertNotEqual(response.data['detail'], "You cannot delete a doctor.", 
                          "Traditional Chinese translation for error message not found")
    
    def test_delete_doctor_message_zh_hans(self):
        """Test the error message when deleting a doctor with Simplified Chinese language header"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='zh-hans')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Check that the message is not the English version
        # This test assumes translations have been set up
        self.assertNotEqual(response.data['detail'], "You cannot delete a doctor.", 
                          "Simplified Chinese translation for error message not found")
    
    def test_doctor_retrieve_language_fields(self):
        """Test that language fields in doctor detail response are translated"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        
        # Test with English
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response_en = self.client.get(url)
        self.assertEqual(response_en.status_code, status.HTTP_200_OK)
        self.assertEqual(response_en.data['language_name'], "English")
        
        # Test with Traditional Chinese
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='zh-hant')
        response_zh_hant = self.client.get(url)
        self.assertEqual(response_zh_hant.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_zh_hant.data['language_name'], "English")
        
        # Test with Simplified Chinese
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='zh-hans')
        response_zh_hans = self.client.get(url)
        self.assertEqual(response_zh_hans.status_code, status.HTTP_200_OK)

        self.assertNotEqual(response_zh_hans.data['language_name'], "English")
    
    def test_language_switching_within_session(self):
        """Test switching languages within the same client session"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        
        # First request with English
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response_en = self.client.get(url)
        english_language_name = str(response_en.data['language_name'])
        
        # Switch to Traditional Chinese
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='zh-hant')
        response_zh = self.client.get(url)
        chinese_language_name = str(response_zh.data['language_name'])
        
        # Switch back to English
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response_en_again = self.client.get(url)
        english_language_name_again = str(response_en_again.data['language_name'])
        
        # First and third responses should be the same (both English)
        self.assertEqual(english_language_name, english_language_name_again)
        
        # If translations are set up, the Traditional Chinese response should differ
        self.assertNotEqual(english_language_name, chinese_language_name)
    
    def test_different_clients_different_languages(self):
        """Test different clients using different languages simultaneously"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        
        # First client uses English
        client_en = APIClient()
        client_en.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response_en = client_en.get(url)
        
        # prevents the language name from being a gettext object
        language_name_en = str(response_en.data['language_name'])
        
        # Second client uses Traditional Chinese
        client_zh = APIClient()
        client_zh.credentials(HTTP_ACCEPT_LANGUAGE='zh-hant')
        response_zh = client_zh.get(url)

        # prevents the language name from being a gettext object
        language_name_zh = str(response_zh.data['language_name'])

        # Both should get a successful response
        self.assertEqual(response_en.status_code, status.HTTP_200_OK)
        self.assertEqual(response_zh.status_code, status.HTTP_200_OK)
        
        # If translations are set up, the language names should differ
        self.assertNotEqual(language_name_en, language_name_zh)
    
    def test_unsupported_language_fallback(self):
        """Test that unsupported language falls back to default language"""
        url = reverse('doctor-detail', args=[self.doctor.id])
        
        # English (supported) as reference
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='en')
        response_en = self.client.get(url)
        
        # French (presumably unsupported)
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='fr')
        response_fr = self.client.get(url)
        
        # Both should work and French should fallback to default language (English)
        self.assertEqual(response_en.status_code, status.HTTP_200_OK)
        self.assertEqual(response_fr.status_code, status.HTTP_200_OK)
        self.assertEqual(response_en.data['language_name'], response_fr.data['language_name']) 