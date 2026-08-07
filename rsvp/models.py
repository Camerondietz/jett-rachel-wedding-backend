from django.db import models


class Guest(models.Model):
    class Attendance(models.TextChoices):
        PENDING = "pending", "Pending"
        WELCOME_AND_WEDDING = "welcome_and_wedding", "Accepts - Welcome Party & Wedding"
        WEDDING_ONLY = "wedding_only", "Accepts - Wedding only"
        DECLINED = "declined", "Declines"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    attendance = models.CharField(max_length=32, choices=Attendance.choices, default=Attendance.PENDING)
    notes = models.TextField(blank=True, help_text="Message left by this guest when they RSVP'd")
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()
