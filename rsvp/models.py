from django.db import models


class Party(models.Model):
    """A household/invitation group that RSVPs together."""

    label = models.CharField(max_length=200, blank=True, help_text="e.g. 'The Smith Family' (admin reference only)")
    notes = models.TextField(blank=True, help_text="Message left by the guests when they RSVP'd")
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.label or f"Party {self.pk}"


class Guest(models.Model):
    class Attendance(models.TextChoices):
        PENDING = "pending", "Pending"
        ATTENDING = "attending", "Attending"
        DECLINED = "declined", "Declined"

    MEAL_CHOICES = [
        ("", "No preference"),
        ("Chicken", "Chicken"),
        ("Beef", "Beef"),
        ("Fish", "Fish"),
        ("Vegetarian", "Vegetarian"),
    ]

    party = models.ForeignKey(Party, related_name="guests", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    attendance = models.CharField(max_length=10, choices=Attendance.choices, default=Attendance.PENDING)
    meal_choice = models.CharField(max_length=20, choices=MEAL_CHOICES, blank=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()
