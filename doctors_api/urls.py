from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, DistrictViewSet, CategoryViewSet

# urlpatterns = [
#     path('doctor/', DoctorViewSet.as_view({'get': 'list'}), name='doctor-list'),
#     path('doctor/<int:pk>/', DoctorViewSet.as_view({'get': 'retrieve'}), name='doctor-detail'),
# ]

router = DefaultRouter()
router.register(r'doctor', DoctorViewSet)
router.register(r'district', DistrictViewSet)
router.register(r'category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]