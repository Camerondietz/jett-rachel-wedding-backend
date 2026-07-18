from django.contrib import admin

from .models import Guest, Party


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 1


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("label", "guest_count", "attending_count", "declined_count", "responded_at")
    search_fields = ("label", "guests__first_name", "guests__last_name")
    inlines = [GuestInline]

    @admin.display(description="Guests")
    def guest_count(self, obj):
        return obj.guests.count()

    @admin.display(description="Attending")
    def attending_count(self, obj):
        return obj.guests.filter(attendance=Guest.Attendance.ATTENDING).count()

    @admin.display(description="Declined")
    def declined_count(self, obj):
        return obj.guests.filter(attendance=Guest.Attendance.DECLINED).count()


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "party", "attendance", "meal_choice")
    list_filter = ("attendance", "meal_choice")
    search_fields = ("first_name", "last_name")
    autocomplete_fields = ["party"]
