from django import forms
from .models import Medical_Claim, Approved_Medical_Claim, Rejected_Medical_Claim

class MedicalClaimForm(forms.ModelForm):
    class Meta:
        model = Medical_Claim
        fields = ["amount","beneficier", "file"]

class ApproveMedicalForm(forms.ModelForm):
    class Meta:
        model = Approved_Medical_Claim
        fields = ["amount", "receipt"]

class RejectMedicalForm(forms.ModelForm):
    class Meta:
        model = Rejected_Medical_Claim
        fields = ["reason"]
