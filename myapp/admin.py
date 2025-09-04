from django.contrib import admin
from .models import Recepie

@admin.register(Recepie)
class RecepieAdmin(admin.ModelAdmin):
    list_display = ("id", "recepie_name", "recepie_description", "recepie_image")
    search_fields = ("recepie_name", "recepie_description")
