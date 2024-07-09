from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from .models import Claim, Claim_Status, Approved_Claim, Rejected_Claim
from .forms import ClaimForm, ApproveForm, RejectForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count
from django.http import Http404
import datetime

# Constants
MONTH_NAMES = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

ACCOMMODATION_CHOICE = {
    0: 'Online',
    1: 'Provided',
    2: 'Not provided'
}

MEAL_CHOICE = {
    0: 'Online',
    1: 'Provided',
    2: 'Not provided',
}

# Long work hours > 8 hours
SHORT_WORK_HOURS = 4
SHORT_WORK_AMOUNT = 50.0
LONG_WORK_AMOUNT = 100.0 
SHORT_MEAL_AMOUNT = 30.0
LONG_MEAL_AMOUNT = 60.0

# Methods
def calculate_amounts(user, claim):
    # Work hours calculation
    date_1 = claim.program_start_date
    date_2 = claim.program_end_date

    diff = date_2 - date_1

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600

    claim.work_hours = hours

    work_hours = divmod(hours, 24)

    # Check if user is staff
    is_staff = user.groups.filter(name="Staff").exists()

    #Exco's calculation
    if claim.program_mode == "Online":
        claim.work_amount = SHORT_WORK_AMOUNT
        claim.meal_amount = 0

    if claim.program_mode == "Physical":
        if hours <= SHORT_WORK_HOURS:
            claim.work_amount = SHORT_WORK_AMOUNT

            if claim.meal_choice == 2:
                claim.meal_amount = 30
        else:
            # Work Allowance Calculation
            claim.work_amount = LONG_WORK_AMOUNT * work_hours[0]
            if work_hours[1] <= SHORT_WORK_HOURS:
                claim.work_amount += SHORT_WORK_AMOUNT
            else:
                claim.work_amount += LONG_WORK_AMOUNT

            # Meal Allowance Calculatioon
            if claim.meal_choice == 2:
                claim.meal_amount = (LONG_MEAL_AMOUNT * work_hours[0])
                if work_hours[1] <= SHORT_WORK_HOURS:
                    claim.meal_amount += SHORT_MEAL_AMOUNT
                else:
                    claim.meal_amount += LONG_MEAL_AMOUNT

    # Travel amount calculations
    claim.travel_amount = float(claim.travel_amount) * 0.80
    
    claim.total_amount = (
        float(claim.work_amount) +
        float(claim.travel_amount) +
        float(claim.accommodation_amount) +
        float(claim.meal_amount) +
        float(claim.toll_amount) +
        float(claim.parking_amount) +
        float(claim.plane_ticket_amount) +
        float(claim.other_amount)
    )

# View functions
def claim_dashboard(request):
    current_year = datetime.datetime.now().year
    claims = Claim.objects.filter(claimer=request.user.id, claim_year=current_year)

    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2, claim_year=current_year)
    rejected_claims = claims.filter(claim_status=3, claim_year=current_year)

    approved_claims_obj = Approved_Claim.objects.filter(claim__in=approved_claims)

    # Total claims
    pending_claims_count = pending_claims.count()
    approved_claims_count = approved_claims.count()
    rejected_claims_count = rejected_claims.count()

    # Claims by month initialization
    pending_claims_by_month = {month: [] for month in range(1, 13)}
    approved_claims_by_month = {month: [] for month in range(1, 13)}

    total_pending_amount_by_month = {month: [] for month in range(1, 13)}
    total_approved_amount_by_month = {month: [] for month in range(1, 13)}

    # Retrieve claims and organize them by month and status
    for month in range(1, 13):
        month_pending_claims = pending_claims.filter(claim_month=month, claim_year=current_year)
        month_approved_claims = approved_claims.filter(claim_month=month, claim_year=current_year)

        pending_claims_by_month[month] = list(month_pending_claims)
        approved_claims_by_month[month] = list(month_approved_claims)

        total_pending_amount_by_month[month] = month_pending_claims.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_approved_amount_by_month[month] = approved_claims_obj.filter(claim__in=month_approved_claims).aggregate(Sum('amount'))['amount__sum'] or 0

    # Total amount 
    total_pending_amount = claims.filter(claim_status=1).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_approved_amount = approved_claims_obj.aggregate(Sum('amount'))['amount__sum'] or 0

    month_names = MONTH_NAMES

    context = {
        'current_year': current_year,
        'month_names': month_names,

        'pending_claims_count': pending_claims_count,
        'approved_claims_count': approved_claims_count,
        'rejected_claims_count': rejected_claims_count,

        'rejected_claims': rejected_claims,

        'total_pending_amount': total_pending_amount,
        'total_approved_amount': total_approved_amount,

        'pending_claims_by_month': pending_claims_by_month,
        'approved_claims_by_month': approved_claims_by_month,

        'total_pending_amount_by_month': total_pending_amount_by_month,
        'total_approved_amount_by_month': total_approved_amount_by_month,
    }
    
    return render(request, 'claim/claim_dashboard.html', context)

def claim_submit(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_bound:  # Check if form is bound
            print("TEST")
            claim = form.save(commit=False)
            claim.claimer = request.user  # Set the claimer before validation
            form.instance = claim  # Update the form's instance

            if form.is_valid():
                try:
                    print("TEST2")
                    claim_status, created = Claim_Status.objects.get_or_create(status="Pending")
                    claim.claim_status = claim_status

                    # Amount Calculation
                    calculate_amounts(request.user, claim)
                
                    claim.save()
                    messages.success(request, 'Claim submitted successfully.')
                    return render(request, 'claim/claim_submit.html', {
                        "success": True})
                except ValidationError as e:
                    for error in e:
                        form.add_error(None, error)
    else:
        form = ClaimForm()

    context = {
        'form': form
    }

    return render(request, 'claim/claim_submit.html', context)

def claim_detail(request, claim_id):
    claim = Claim.objects.get(pk=claim_id)

    if not request.user.is_authenticated or (request.user.id != claim.claimer.id and not request.user.is_staff):
        raise Http404("You are not authorized to access this file.")
    
    is_Pending = False
    is_Approved = False
    is_Rejected = False

    if claim.claim_status.id == 1:
        is_Pending = True
    elif claim.claim_status.id == 2:
        is_Approved = True
    else:
        is_Rejected = True

    approveForm = ApproveForm(prefix="approved")
    rejectForm = RejectForm(prefix="rejected")

    if request.method == 'POST':
        if 'approve' in request.POST:
            approveForm = ApproveForm(request.POST, request.FILES, prefix="approved")
            if approveForm.is_valid():
                instance = approveForm.save(commit=False)
                instance.claim = claim
                claim_status, created = Claim_Status.objects.get_or_create(status="Approved")
                claim.claim_status = claim_status
                claim.save()
                instance.save()
                return redirect('mitasa_admin:dashboard')
        elif 'reject' in request.POST:
            rejectForm = RejectForm(request.POST, prefix="rejected")
            if rejectForm.is_valid():
                instance = rejectForm.save(commit=False)
                instance.claim = claim
                claim_status, created = Claim_Status.objects.get_or_create(status="Rejected")
                claim.claim_status = claim_status
                claim.save()
                instance.save()
                return redirect('mitasa_admin:dashboard')
        else:
            approveForm = ApproveForm(prefix="approved")
            rejectForm = RejectForm(prefix="rejected")

    month_names = MONTH_NAMES
    accommodation_choice = ACCOMMODATION_CHOICE
    meal_choice = MEAL_CHOICE

    context = {
        'claim': claim,

        'month_names': month_names,
        'accommodation_choice': accommodation_choice,
        'meal_choice': meal_choice,

        'is_Pending': is_Pending,
        'is_Approved': is_Approved,
        'is_Rejected': is_Rejected,

        'approveForm': approveForm,
        'rejectForm': rejectForm,
    }
    
    return render(request, 'detail.html', context)

def claim_delete(request, claim_id):
    if request.method == 'POST':
        claim = Claim.objects.get(pk=claim_id)
        claim.delete()
    
    return HttpResponseRedirect(reverse('claim:dashboard'))

def claim_history(request):
    claims = Claim.objects.filter(claimer=request.user)

    claims_by_year_list = claims.values('claim_year').annotate(total_claims=Count('id')).annotate(total_approved_claims=Count('approved_claim__claim_id')).annotate(total_approved_amount=Sum('approved_claim__amount')).order_by('claim_year')

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

    return render(request,'claim/claim_history.html', context)

def history_dashboard(request, year):
    # List of all the claims
    claims = Claim.objects.filter(claimer=request.user, claim_year=year)
    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2)
    rejected_claims = claims.filter(claim_status=3)

    # Total claims
    pending_claims_count = pending_claims.count()
    approved_claims_count = approved_claims.count()
    rejected_claims_count = rejected_claims.count()

    # Claims by month initialization
    pending_claims_by_month = {month: [] for month in range(1, 13)}
    approved_claims_by_month = {month: [] for month in range(1, 13)}

    total_pending_amount_by_month = {month: [] for month in range(1, 13)}
    total_approved_amount_by_month = {month: [] for month in range(1, 13)}

    # Retrieve claims and organize them by month and status
    for month in range(1, 13):
        month_pending_claims = pending_claims.filter(claim_month=month)
        month_approved_claims = approved_claims.filter(claim_month=month)

        pending_claims_by_month[month] = list(month_pending_claims)
        approved_claims_by_month[month] = list(month_approved_claims)

        total_pending_amount_by_month[month] = month_pending_claims.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_approved_amount_by_month[month] = approved_claims.filter(id__in=month_approved_claims).aggregate(Sum('approved_claim__amount'))['approved_claim__amount__sum'] or 0

    # Total amount 
    total_pending_amount = pending_claims.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_approved_amount = approved_claims.aggregate(Sum('approved_claim__amount'))['approved_claim__amount__sum'] or 0

    context = {
        'history': True,
        'year': year,
        'month_names': MONTH_NAMES,

        'pending_claims_count': pending_claims_count,
        'approved_claims_count': approved_claims_count,
        'rejected_claims_count': rejected_claims_count,

        'rejected_claims': rejected_claims,

        'total_pending_amount': total_pending_amount,
        'total_approved_amount': total_approved_amount,

        'pending_claims_by_month': pending_claims_by_month,
        'approved_claims_by_month': approved_claims_by_month,

        'total_pending_amount_by_month': total_pending_amount_by_month,
        'total_approved_amount_by_month': total_approved_amount_by_month,
    }

    return render(request, 'claim/history_dashboard.html', context)