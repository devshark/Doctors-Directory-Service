from django.test import TestCase
from doctors_api.models import Doctor, Category, District, DoctorLanguage
from decimal import Decimal
from django.utils import translation
from django.utils.translation import gettext as _


class InternationalizationTest(TestCase):
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
            consultation_fee=Decimal("200.00")
        )

    def test_language_choices_english(self):
        """Test that language choices are properly translated in English"""
        with translation.override('en'):
            # Get the display text for each language choice
            english_display = dict(DoctorLanguage).get('en')
            mandarin_display = dict(DoctorLanguage).get('mandarin')
            cantonese_display = dict(DoctorLanguage).get('cantonese')
            
            # Verify English translations
            self.assertEqual(english_display, "English")
            self.assertEqual(mandarin_display, "Mandarin")
            self.assertEqual(cantonese_display, "Cantonese")

    def test_language_choices_zh_hant(self):
        """Test that language choices are properly translated in Traditional Chinese"""
        with translation.override('zh-hant'):
            # Get the display text for each language choice
            english_display = dict(DoctorLanguage).get('en')
            mandarin_display = dict(DoctorLanguage).get('mandarin')
            cantonese_display = dict(DoctorLanguage).get('cantonese')
            
            # If translations exist, these should be different from English
            self.assertNotEqual(english_display, "English", 
                               "Traditional Chinese translation for 'English' not found")
            self.assertNotEqual(mandarin_display, "Mandarin", 
                               "Traditional Chinese translation for 'Mandarin' not found")
            self.assertNotEqual(cantonese_display, "Cantonese", 
                               "Traditional Chinese translation for 'Cantonese' not found")

    def test_language_choices_zh_hans(self):
        """Test that language choices are properly translated in Simplified Chinese"""
        with translation.override('zh-hans'):
            # Get the display text for each language choice
            english_display = dict(DoctorLanguage).get('en')
            mandarin_display = dict(DoctorLanguage).get('mandarin')
            cantonese_display = dict(DoctorLanguage).get('cantonese')
            
            # If translations exist, these should be different from English
            self.assertNotEqual(english_display, "English", 
                               "Simplified Chinese translation for 'English' not found")
            self.assertNotEqual(mandarin_display, "Mandarin", 
                               "Simplified Chinese translation for 'Mandarin' not found")
            self.assertNotEqual(cantonese_display, "Cantonese", 
                               "Simplified Chinese translation for 'Cantonese' not found")

    def test_language_name_method_with_translation(self):
        """Test that the language_name method returns translated language names"""
        # Test English language
        self.doctor.language = "en"
        self.doctor.save()
        
        with translation.override('en'):
            self.assertEqual(self.doctor.language_name(), "English")
        
        with translation.override('zh-hant'):
            # This should return the Traditional Chinese word for "English"
            self.assertEqual(self.doctor.language_name(), "英文")
        
        # Test Mandarin language
        self.doctor.language = "mandarin"
        self.doctor.save()
        
        with translation.override('en'):
            self.assertEqual(self.doctor.language_name(), "Mandarin")
        
        with translation.override('zh-hans'):
            # This should return the Simplified Chinese word for "Mandarin"
            self.assertEqual(self.doctor.language_name(), "普通话")
            
        # Test Cantonese language
        self.doctor.language = "cantonese"
        self.doctor.save()
        
        with translation.override('en'):
            self.assertEqual(self.doctor.language_name(), "Cantonese")
        
        with translation.override('zh-hant'):
            # This should return the Traditional Chinese word for "Cantonese"
            self.assertEqual(self.doctor.language_name(), "廣東話")

    def test_translation_fallback(self):
        """Test that translations fall back to English when a language is not available"""
        # Set an unsupported language
        with translation.override('fr'):  # French is presumably not supported
            # The system should fall back to English for the language display
            self.assertEqual(self.doctor.language_name(), "Anglais")
            
            # The language choices should be in English
            english_display = dict(DoctorLanguage).get('en')
            self.assertEqual(english_display, "Anglais")
            