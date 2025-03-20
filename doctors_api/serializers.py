from rest_framework import serializers
from .models import Doctor, District, Category
import logging

logger = logging.getLogger(__name__)

class DoctorSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    language_name = serializers.SerializerMethodField()
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    
    class Meta:
        model = Doctor
        fields = [
            'id', 
            'name', 
            'category', 
            'category_name', 
            'address', 
            'contact_details', 
            'district', 
            'district_name', 
            'consultation_fee', 
            'language',
            'language_name'
            ]
        read_only_fields = ['id']
        
    def get_category_name(self, obj):
        return obj.category.name

    def get_district_name(self, obj):
        return obj.district.name
    
    def get_language_name(self, obj):
        return obj.language_name()

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id']
