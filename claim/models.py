from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import datetime

# File path of files uploaded during claim submission.
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.claimer.id, filename)

# File path of receipt files
def claim_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.claim.claimer.id, filename)

class Claim_Status(models.Model):
    status = models.CharField(max_length=10)
    
    def __str__(self):
        return self.status

class Claim(models.Model):
    accommodation_choices = [
        (0, "Online"),  
        (1, "Provided"),
        (2, "Not provided"),
    ]

    meal_choices = [
        (0, ""),
        (1, "Provided"),
        (2, "Not provided")
    ]

    month_choices = [(1, "January"),
                     (2, "February"),
                     (3, "March"),
                     (4, "April"),
                     (5, "May"),
                     (6, "June"),
                     (7, "July"),
                     (8, "August"),
                     (9, "September"),
                     (10, "October"),
                     (11, "November"),
                     (12, "December"),]
    
    mode_choices = [
        ("", ""),
        ("Online", "Online"),
        ("Physical", "Physical")
    ]
    
    claimer = models.ForeignKey(User, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=200)
    program_start_date = models.DateTimeField()
    program_end_date = models.DateTimeField()
    program_mode = models.CharField(choices=mode_choices, max_length=10, default="")
    program_location = models.TextField()
    program_letter_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    claim_month = models.IntegerField(choices=month_choices, default=0)
    claim_year = models.IntegerField(default=datetime.datetime.now().year)

    work_hours = models.IntegerField(default=0)
    work_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)

    travel_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    travel_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    accommodation_choice = models.IntegerField(choices=accommodation_choices, default=0)
    accommodation_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    accommodation_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    meal_choice = models.IntegerField(choices=meal_choices, default=0)
    meal_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    meal_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    toll_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    toll_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    parking_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    parking_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    plane_ticket_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    plane_ticket_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    other_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    other_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    total_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    
    created_at = models.DateField(auto_now_add=True)
    claim_status = models.ForeignKey(Claim_Status, on_delete=models.SET_NULL, null=True)

    def clean(self):
        # Check if any existing claims have the same program start and end dates for the same claimer
        if Claim.objects.filter(
            claimer=self.claimer_id,
            program_start_date=self.program_start_date,
            program_end_date=self.program_end_date
        ).exclude(pk=self.pk).exists():
            raise ValidationError("A claim for the same program dates and times already exists.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Claimer: {self.claimer.username} | Program Name: {self.program_name} | Created At: {self.created_at}'
    
class Approved_Claim(models.Model):
    claim = models.OneToOneField(Claim, primary_key=True, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    receipt = models.FileField(upload_to=claim_directory_path, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Claimer: {self.claim.claimer.username} | Program Name: {self.claim.program_name} | Approved At: {self.created_at}'
    
class Rejected_Claim(models.Model):
    claim = models.OneToOneField(Claim, primary_key=True, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Claimer: {self.claim.claimer.username} | Program Name: {self.claim.program_name} | Approved At: {self.created_at}'