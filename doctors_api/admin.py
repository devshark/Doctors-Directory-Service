from django.contrib import admin
from .models import Doctor, Category, District

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Category)
admin.site.register(District)

