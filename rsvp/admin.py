from django.contrib import admin

from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "attendance", "short_notes", "responded_at")
    list_filter = ("attendance",)
    search_fields = ("first_name", "last_name", "notes")
    readonly_fields = ("responded_at",)

    @admin.display(description="Notes")
    def short_notes(self, obj):
        if len(obj.notes) <= 60:
            return obj.notes
        return obj.notes[:60] + "..."
