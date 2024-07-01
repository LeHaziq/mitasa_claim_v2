from django.contrib import admin
from .models import Medical_Claim, Approved_Medical_Claim, Rejected_Medical_Claim

admin.site.register(Medical_Claim)
admin.site.register(Approved_Medical_Claim)
admin.site.register(Rejected_Medical_Claim)
