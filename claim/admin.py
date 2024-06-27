from django.contrib import admin
from .models import Claim, Claim_Status, Approved_Claim, Rejected_Claim
# Register your models here.

admin.site.register(Claim)
admin.site.register(Claim_Status)
admin.site.register(Approved_Claim)
admin.site.register(Rejected_Claim)