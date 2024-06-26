from django.shortcuts import render
from .models import Claim, Claim_Status
from .forms import ClaimForm
from django.contrib import messages
from django.core.exceptions import ValidationError

# Constants
# Long work hours > 8 hours
SHORT_WORK_HOURS = 4
SHORT_WORK_AMOUNT = 50.0
LONG_WORK_AMOUNT = 100.0 
SHORT_MEAL_AMOUNT = 30.0
LONG_MEAL_AMOUNT = 60.0

# Methods
def calculate_amounts(request, claim):
    # Work hours calculation
    date_1 = claim.program_start_date
    date_2 = claim.program_end_date

    diff = date_2 - date_1

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600

    claim.work_hours = hours

    work_hours = divmod(hours, 24)

    # Check if user is staff
    is_staff = request.user.groups.filter(name="Staff").exists()

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

# View functions
def claim_dashboard(request):

    context = {

    }
    return render(request, 'claim/claim_dashboard.html', context)

def claim_submit(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.claimer = request.user
            claim_status, created = Claim_Status.objects.get_or_create(status="Pending")
            claim.claim_status = claim_status

            # Amount Calculation
            calculate_amounts(request, claim)

            try:
                claim.save()
                messages.success(request, 'Claim submitted successfully.')
                return render(request, 'claim/claim_submit.html', {
                    "success": True})
            except ValidationError as e:
                for error in e:
                    form.add_error(None, error)

            return render(request, 'claim/claim_submit.html', {
                "success": True})
        else:
            print(form.errors)
    else:
        form = ClaimForm()

    context = {
        'form': form
    }

    return render(request, 'claim/claim_submit.html', context)