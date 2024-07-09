from django import forms
from .models import Claim, Approved_Claim, Rejected_Claim

class ClaimForm(forms.ModelForm):
    program_start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    program_end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    
    class Meta:
        model = Claim
        fields = ["program_name", "program_start_date", "program_end_date","program_mode", "claim_month", "claim_year", "program_location", "program_letter_file","accommodation_choice", "accommodation_amount", "accommodation_file", "travel_distance", "travel_file","meal_choice","meal_file", "toll_amount","toll_file", "parking_amount","parking_file", "plane_ticket_amount","plane_ticket_file", "other_amount","other_file"]
        widgets = {
            "program_letter_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "accommodation_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "travel_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "toll_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "parking_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "plane_ticket_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            "other_file": forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}),
        }

class ApproveForm(forms.ModelForm):
    class Meta:
        model = Approved_Claim
        fields = ["amount", "receipt"]

class RejectForm(forms.ModelForm):
    class Meta:
        model = Rejected_Claim
        fields = ["reason"]

