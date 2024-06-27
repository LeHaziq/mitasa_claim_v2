from django.shortcuts import render
from .models import Medical_Claim
from django.db.models import Sum, Count
from .models import YEARLY_LIMIT as YEARLY_CLAIM_LIMIT
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

    claim_limit_percentage = claim_limit / yearly_limit * 100

    context = {
        'is_staff': True,
        'claim_limit': claim_limit,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount,
    }
    return render(request, 'medical_claim/medical_dashboard.html', context)