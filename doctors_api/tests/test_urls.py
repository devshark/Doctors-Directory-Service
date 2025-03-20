from rest_framework.test import APITestCase
from django.urls import reverse, resolve
from doctors_api.views import DoctorViewSet, CategoryViewSet, DistrictViewSet

class UrlTestCase(APITestCase):
    def test_list_doctors(self):
        url = reverse('doctor-list')
        self.assertEqual(resolve(url).func.cls, DoctorViewSet)

    def test_list_categories(self):
        url = reverse('category-list')
        self.assertEqual(resolve(url).func.cls, CategoryViewSet)

    def test_list_districts(self):
        url = reverse('district-list')
        self.assertEqual(resolve(url).func.cls, DistrictViewSet)
        
    def test_retrieve_doctor(self):
        url = reverse('doctor-detail', args=['1'])
        self.assertEqual(resolve(url).func.cls, DoctorViewSet)

    def test_retrieve_category(self):
        url = reverse('category-detail', args=['1'])
        self.assertEqual(resolve(url).func.cls, CategoryViewSet)

    def test_retrieve_district(self):
        url = reverse('district-detail', args=['1'])
        self.assertEqual(resolve(url).func.cls, DistrictViewSet)
