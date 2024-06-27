from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from claim.models import Claim_Status
import datetime

YEARLY_LIMIT = 3000

BENEFICIERY_CHOICES = [
    ("Myself", "Myself"),
    ("Husband", "Husband"),
    ("Children", "Children")
]

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.claimer.id, filename)

# File path of receipt files
def claim_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.claim.claimer.id, filename)

class Medical_Claim(models.Model):
    claimer = models.ForeignKey(User, on_delete=models.CASCADE)
    beneficier = models.CharField(choices=BENEFICIERY_CHOICES, max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    claim_year = models.IntegerField(default=datetime.datetime.now().year)
    claim_status = models.ForeignKey(Claim_Status, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        current_year = timezone.now().year

        pending_claims = Medical_Claim.objects.filter(
            claimer=self.claimer_id,
            claim_status=1,
            created_at__year= current_year
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        approved_claims = Medical_Claim.objects.filter(
            claimer=self.claimer_id,
            claim_status=2,
            created_at__year= current_year
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        total_claimed = pending_claims + approved_claims

        if total_claimed + self.amount > YEARLY_LIMIT:
            raise ValidationError(f'You have exceeded your claim limit for the year. Yearly Limit: RM{YEARLY_LIMIT}, Total claimed: RM{total_claimed}, Attempted claim: RM{self.amount}')

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method to perform validation
        super().save(*args, **kwargs)

class Approved_Medical_Claim(models.Model):
    claim = models.OneToOneField(Medical_Claim, primary_key=True, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    receipt = models.FileField(upload_to=claim_directory_path, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Claimer: {self.claim.claimer.username} | Approved At: {self.created_at}'
    
class Rejected_Medical_Claim(models.Model):
    claim = models.OneToOneField(Medical_Claim, primary_key=True, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Claimer: {self.claim.claimer.username} | Approved At: {self.created_at}'