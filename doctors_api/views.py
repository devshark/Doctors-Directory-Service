from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from .models import Doctor, District, Category
from .serializers import DoctorSerializer, DistrictSerializer, CategorySerializer
from django.utils.translation import gettext as _
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)
class DoctorFilter(FilterSet):
    min_consultation_fee = NumberFilter(field_name="consultation_fee", lookup_expr='gte')
    max_consultation_fee = NumberFilter(field_name="consultation_fee", lookup_expr='lte')
    category = NumberFilter(field_name="category__id")
    district = NumberFilter(field_name="district__id")
    language = CharFilter(field_name="language", lookup_expr='iexact')

    class Meta:
        model = Doctor
        fields = [
            'min_consultation_fee', 
            'max_consultation_fee', 
            'category', 
            'district', 
            'language'
            ]
        
class DoctorViewSet(
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DoctorFilter
    search_fields = ['category__name', 'district__name', 'language']
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DistrictViewSet(
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class CategoryViewSet(
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer