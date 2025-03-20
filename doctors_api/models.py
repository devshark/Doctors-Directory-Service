from django.db import models
from django.utils.translation import gettext_lazy as _
import logging

DoctorLanguage = (
    ('en', _('English')),
    ('mandarin', _('Mandarin')),
    ('cantonese', _('Cantonese')),
)

logger = logging.getLogger(__name__)

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

    def __str__(self):
        return self.name

# Create your models here.
class Doctor(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255) # phone, email, etc. multi-valued. should be reconstructed if needed for analysis.
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    language = models.CharField(max_length=10, choices=DoctorLanguage) # should be reconstructed if needed for analysis.
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True) # 1 for active, 0 for inactive
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def category_name(self):
        return self.category.name

    def district_name(self):
        return self.district.name

    def language_name(self):
        return next((lang[1] for lang in DoctorLanguage if lang[0] == self.language), None)
        
    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    def restore(self, *args, **kwargs):
        self.is_active = True
        self.save()

    def queryset(self):
        return self.objects.filter(is_active=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
