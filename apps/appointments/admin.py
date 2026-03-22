from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = ("patient", "provider", "scheduled_at", "duration", "status")
    list_filter = ("status", "provider")
    search_fields = ("patient__name", "reason", "notes")
    date_hierarchy = "scheduled_at"

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
