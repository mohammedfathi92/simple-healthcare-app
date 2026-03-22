from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = ("name", "provider", "phone", "email", "created_at")
    list_filter = ("provider",)
    search_fields = ("name", "phone", "email")

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
