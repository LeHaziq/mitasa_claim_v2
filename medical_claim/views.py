from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
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

    claim_limit_percentage = 100 - math.ceil(claim_limit / yearly_limit * 100)

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

def medical_detail(request, claim_id):
    claim = Medical_Claim.objects.get(pk=claim_id)

    is_Pending = False
    is_Approved = False
    is_Rejected = False

    if claim.claim_status.id == 1:
        is_Pending = True
    if claim.claim_status.id == 2:
        is_Approved = True
    if claim.claim_status.id == 3:
        is_Rejected = True

    is_admin = False
    if request.user.is_staff:
        is_admin = True

    approveForm = ApproveMedicalForm(prefix="approved")
    rejectForm = RejectMedicalForm(prefix="rejected")

    if request.method == 'POST':
        if 'approve' in request.POST:
            approveForm = ApproveMedicalForm(request.POST, request.FILES, prefix="approved")
            if approveForm.is_valid():
                instance = approveForm.save(commit=False)
                instance.claim = claim
                claim_status, created = Claim_Status.objects.get_or_create(status="Approved")
                claim.claim_status = claim_status
                claim.save()
                instance.save()
                return redirect('mitasa_admin:medical_dashboard')
        elif 'reject' in request.POST:
            rejectForm = RejectMedicalForm(request.POST, prefix="rejected")
            if rejectForm.is_valid():
                instance = rejectForm.save(commit=False)
                instance.claim = claim
                claim_status, created = Claim_Status.objects.get_or_create(status="Rejected")
                claim.claim_status = claim_status
                claim.save()
                instance.save()
                return redirect('mitasa_admin:medical_dashboard')
        else:
            approveForm = ApproveMedicalForm(prefix="approved")
            rejectForm = RejectMedicalForm(prefix="rejected")

    context = {
        'claim': claim,

        'is_Pending': is_Pending,
        'is_Approved': is_Approved,
        'is_Rejected': is_Rejected,

        'is_admin': is_admin,

        'approveForm': approveForm,
        'rejectForm': rejectForm,
    }
    return render(request, 'medical_claim/medical_detail.html', context)

def medical_history(request):
    claims = Medical_Claim.objects.filter(claimer=request.user)

    claims_by_year_list = claims.values('claim_year').annotate(total_claims=Count('id')).annotate(total_approved_claims=Count('approved_medical_claim__claim_id')).annotate(total_approved_amount=Sum('approved_medical_claim__amount')).order_by('claim_year')

    overall_claims = 0
    overall_approved_claims = 0
    overall_approved_amount = 0

    for claim in claims_by_year_list:
        overall_claims += (claim['total_claims']) or 0
        overall_approved_claims += (claim['total_approved_claims']) or 0
        overall_approved_amount += (claim['total_approved_amount']) or 0

    context = {
        'claims_by_year_list': claims_by_year_list,
        'overall_claims': overall_claims,
        'overall_approved_claims': overall_approved_claims,
        'overall_approved_amount': overall_approved_amount,
    }

    return render(request, 'medical_claim/medical_history.html', context)

def medical_history_dashboard(request, year):
    claims = Medical_Claim.objects.filter(claimer=request.user, claim_year=year)
    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2)
    rejected_claims = claims.filter(claim_status=3)

    approved_amount = approved_claims.aggregate(Sum("approved_medical_claim__amount"))["approved_medical_claim__amount__sum"] or 0

    context = {
        'is_staff': True,
        'year': year,
        'claims': claims,
        'pending_claims': pending_claims,  
        'approved_claims': approved_claims,  
        'rejected_claims': rejected_claims,
        'approved_amount': approved_amount,
    }

    return render(request, 'medical_claim/medical_history_dashboard.html', context)

