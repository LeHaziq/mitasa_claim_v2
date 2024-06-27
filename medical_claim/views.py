from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Medical_Claim
from django.db.models import Sum, Count
from django.core.exceptions import ValidationError
from claim.models import Claim_Status
from .models import Medical_Claim
from .forms import MedicalClaimForm, ApproveMedicalForm, RejectMedicalForm
from .models import YEARLY_LIMIT as YEARLY_CLAIM_LIMIT
import math
import datetime

# Create your views here.

def medical_dashboard(request):
    current_year = datetime.datetime.now().year

    claims = Medical_Claim.objects.filter(claimer=request.user, claim_year=current_year)
    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2)
    rejected_claims = claims.filter(claim_status=3)

    pending_amount = pending_claims.aggregate(Sum("amount"))["amount__sum"] or 0
    approved_amount = approved_claims.aggregate(Sum("approved_medical_claim__amount"))["approved_medical_claim__amount__sum"] or 0

    yearly_limit = YEARLY_CLAIM_LIMIT
    claim_limit = yearly_limit - (pending_amount + approved_amount)

    claim_limit_percentage = math.ceil(claim_limit / yearly_limit * 100)
    print(type(claim_limit_percentage))

    context = {
        'yearly_limit': yearly_limit,
        'claim_limit': claim_limit,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount,
        'claim_limit_percentage': claim_limit_percentage
    }
    return render(request, 'medical_claim/medical_dashboard.html', context)

def medical_submit(request):
    if not request.user.is_authenticated:
        return HttpResponse("User is not authenticated", status=401)  # Ensure the user is authenticated
    
    if request.method == 'POST':
        form = MedicalClaimForm(request.POST, request.FILES)
        if form.is_bound:  # Check if form is bound
            claim = form.save(commit=False)
            claim.claimer = request.user  # Set the claimer before validation
            form.instance = claim  # Update the form's instance

            if form.is_valid():
                try:
                    claim_status, created = Claim_Status.objects.get_or_create(status="Pending")
                    claim.claim_status = claim_status
                    claim.save()
                    return HttpResponseRedirect(reverse('medical:dashboard'))
                except ValidationError as e:
                    form.add_error(None, e)
    else:
        form = MedicalClaimForm()

    context = {
        'form': form
    }
    return render(request, 'medical_claim/medical_submit.html', context)

