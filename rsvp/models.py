from django.db import models


class Party(models.Model):
    """A household/invitation group that RSVPs together."""

    label = models.CharField(max_length=200, blank=True, help_text="e.g. 'The Smith Family' (admin reference only)")

    def __str__(self):
        return self.label or f"Party {self.pk}"


class Meal(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to stop offering this meal without deleting past RSVPs that used it")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Guest(models.Model):
    class Attendance(models.TextChoices):
        PENDING = "pending", "Pending"
        ATTENDING = "attending", "Attending"
        DECLINED = "declined", "Declined"

    party = models.ForeignKey(Party, related_name="guests", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    attendance = models.CharField(max_length=10, choices=Attendance.choices, default=Attendance.PENDING)
    meal_choice = models.ForeignKey(Meal, null=True, blank=True, on_delete=models.SET_NULL, related_name="guests")
    notes = models.TextField(blank=True, help_text="Message left by this guest when they RSVP'd")
    responded_at = models.DateTimeField(null=True, blank=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()
