from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.models import User
from claim.models import Claim, Approved_Claim
from medical_claim.models import Medical_Claim
from django.db.models import Sum, Count, Q
import simplejson as json
import datetime

from medical_claim.models import YEARLY_LIMIT

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

# Methods
def category_chart(request, year):
    # Aggregate data by month and category
    # Initialize data structure for months and categories
    data = {
        'work': [],
        'travel': [],
        'accommodation': [],
        'meal': [],
        'toll': [],
        'parking': [],
        'plane_ticket': [],
        'other': [],
        'months': [month[1] for month in Claim.month_choices]  # Extract month names
    }

    # Aggregate data for each month
    for month in Claim.month_choices:
        month_num = month[0]
        claims_in_month = Claim.objects.filter(claim_status=2, claim_month=month_num, claim_year=year)
        data['work'].append(claims_in_month.aggregate(Sum('work_amount'))['work_amount__sum'] or 0)
        data['travel'].append(claims_in_month.aggregate(Sum('travel_amount'))['travel_amount__sum'] or 0)
        data['accommodation'].append(claims_in_month.aggregate(Sum('accommodation_amount'))['accommodation_amount__sum'] or 0)
        data['meal'].append(claims_in_month.aggregate(Sum('meal_amount'))['meal_amount__sum'] or 0)
        data['toll'].append(claims_in_month.aggregate(Sum('toll_amount'))['toll_amount__sum'] or 0)
        data['parking'].append(claims_in_month.aggregate(Sum('parking_amount'))['parking_amount__sum'] or 0)
        data['plane_ticket'].append(claims_in_month.aggregate(Sum('plane_ticket_amount'))['plane_ticket_amount__sum'] or 0)
        data['other'].append(claims_in_month.aggregate(Sum('other_amount'))['other_amount__sum'] or 0)

    json_data = json.dumps(data)

    return json_data

# View functions
def admin_dashboard(request):
    if not request.user.is_staff:
        raise Http404("You are not authorized to access this file.")
    
    current_year = datetime.datetime.now().year
    users = User.objects.filter(is_staff=False)
    staffs = users.filter(groups__name="Staff")
    excos = users.filter(groups__name="Exco")

    # List of all the claims
    claims = Claim.objects.all()
    pending_claims = claims.filter(claim_status=1, claim_year=current_year)
    approved_claims = claims.filter(claim_status=2, claim_year=current_year)
    rejected_claims = claims.filter(claim_status=3, claim_year=current_year)

    outstanding_claims = claims.filter(claim_status=1, claim_year=current_year-1)
    total_outstanding_amount = outstanding_claims.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

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

    # Claims by user (Table)
    pending_claims_by_user = claims.filter(claim_status=1).values('claimer__id','claimer__username', 'claimer__first_name').annotate(total=Count("id")).annotate(amount=Sum("total_amount")).order_by('claimer__username')

    # Charts Data
    approved_claims_by_user = approved_claims.values('claimer__first_name').annotate(total=Count("id")).annotate(amount=Sum("approved_claim__amount"))

    # approved_amount_by_month = approved_claims.values('claim_month').annotate(total_amount=Sum('approved_claim__amount')).order_by('claim_month')

    approved_claims_user_data = json.dumps(list(approved_claims_by_user))
    approved_amount_month_data = json.dumps(total_approved_amount_by_month)

    category_data = category_chart(request, current_year)

    month_names = MONTH_NAMES

    context = {
        'current_year': current_year,
        'month_names': month_names,

        'users': users,
        'excos': excos,
        'staffs': staffs,

        'pending_claims_count': pending_claims_count,
        'approved_claims_count': approved_claims_count,
        'rejected_claims_count': rejected_claims_count,

        'outstanding_claims': outstanding_claims,
        'rejected_claims': rejected_claims,

        'total_pending_amount': total_pending_amount,
        'total_outstanding_amount': total_outstanding_amount,
        'total_approved_amount': total_approved_amount,

        'pending_claims_by_month': pending_claims_by_month,
        'approved_claims_by_month': approved_claims_by_month,

        'total_pending_amount_by_month': total_pending_amount_by_month,
        'total_approved_amount_by_month': total_approved_amount_by_month,

        'pending_claims_by_user': pending_claims_by_user,

        # Graphs
        'approved_claims_user_data': approved_claims_user_data,
        'approved_amount_month_data': approved_amount_month_data,
        'category_data': category_data
    }
    return render(request, 'mitasa_admin/admin_dashboard.html', context)

def admin_history(request):
    claims = Claim.objects.all()

    claims_by_year_list = claims.values('claim_year').annotate(total_claims=Count('id')).annotate(total_approved_claims=Count('approved_claim__claim_id')).annotate(total_approved_amount=Sum('approved_claim__amount')).order_by('claim_year')

    overall_claims = 0
    overall_approved_claims = 0
    overall_approved_amount = 0

    for claim in claims_by_year_list:
        overall_claims += (claim['total_claims'])
        overall_approved_claims += (claim['total_approved_claims']) 
        overall_approved_amount += (claim['total_approved_amount'])

    context = {
        'claims_by_year_list': claims_by_year_list,
        'overall_claims': overall_claims,
        'overall_approved_claims': overall_approved_claims,
        'overall_approved_amount': overall_approved_amount,
    }
    return render(request, 'mitasa_admin/admin_history.html', context)

def history_admin_dashboard(request, year):
    if not request.user.is_staff:
        raise Http404("You are not authorized to access this file.")
    
    current_year = year
    users = User.objects.filter(is_staff=False)
    staffs = users.filter(groups__name="Staff")
    excos = users.filter(groups__name="Exco")

    # List of all the claims
    claims = Claim.objects.filter(claim_year=current_year)
    pending_claims = claims.filter(claim_status=1, claim_year=current_year)
    approved_claims = claims.filter(claim_status=2, claim_year=current_year)
    rejected_claims = claims.filter(claim_status=3, claim_year=current_year)

    outstanding_claims = claims.filter(claim_status=1, claim_year=current_year-1)
    total_outstanding_amount = outstanding_claims.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

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

    # Claims by user (Table)
    pending_claims_by_user = claims.filter(claim_status=1).values('claimer__id','claimer__username', 'claimer__first_name').annotate(total=Count("id")).annotate(amount=Sum("total_amount")).order_by('claimer__username')

    # Charts Data
    approved_claims_by_user = approved_claims.values('claimer__first_name').annotate(total=Count("id")).annotate(amount=Sum("approved_claim__amount"))

    # approved_amount_by_month = approved_claims.values('claim_month').annotate(total_amount=Sum('approved_claim__amount')).order_by('claim_month')

    approved_claims_user_data = json.dumps(list(approved_claims_by_user))
    approved_amount_month_data = json.dumps(total_approved_amount_by_month)

    category_data = category_chart(request, current_year)

    month_names = MONTH_NAMES

    context = {
        'current_year': current_year,
        'month_names': month_names,

        'users': users,
        'excos': excos,
        'staffs': staffs,

        'pending_claims_count': pending_claims_count,
        'approved_claims_count': approved_claims_count,
        'rejected_claims_count': rejected_claims_count,

        'outstanding_claims': outstanding_claims,
        'rejected_claims': rejected_claims,

        'total_pending_amount': total_pending_amount,
        'total_outstanding_amount': total_outstanding_amount,
        'total_approved_amount': total_approved_amount,

        'pending_claims_by_month': pending_claims_by_month,
        'approved_claims_by_month': approved_claims_by_month,

        'total_pending_amount_by_month': total_pending_amount_by_month,
        'total_approved_amount_by_month': total_approved_amount_by_month,

        'pending_claims_by_user': pending_claims_by_user,

        # Graphs
        'approved_claims_user_data': approved_claims_user_data,
        'approved_amount_month_data': approved_amount_month_data,
        'category_data': category_data
    }
    return render(request, 'mitasa_admin/history_admin_dashboard.html', context)

def user_dashboard(request, user_id):

    if not request.user.is_staff:
        raise Http404("You are not authorized to access this file.")
    
    current_year = datetime.datetime.now().year

    user = User.objects.get(pk=user_id)

    # List of all the claims
    claims = Claim.objects.filter(claimer=user)
    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2)
    rejected_claims = claims.filter(claim_status=3, claim_year=current_year)

    approved_claims_obj = Approved_Claim.objects.filter(claim__in=claims)

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

    context = {
        'user': user,
        'current_year': current_year,
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
    return render(request, 'mitasa_admin/user_dashboard.html', context)

def medical_dashboard(request):
    if not request.user.is_staff:
        raise Http404("You are not authorized to access this file.")
    
    current_year = datetime.datetime.now().year

    staffs = User.objects.filter(groups__name="Staff")

    claims = Medical_Claim.objects.filter(claim_year=current_year)
    pending_claims = claims.filter(claim_status=1)
    approved_claims = claims.filter(claim_status=2)
    rejected_claims = claims.filter(claim_status=3)

    pending_amount = pending_claims.aggregate(Sum("amount"))["amount__sum"] or 0
    approved_amount = approved_claims.aggregate(Sum("amount"))["amount__sum"] or 0

    pending_claims_by_user = staffs.values('id', 'username', 'first_name').annotate(pending_claims=Count('medical_claim__id', filter=Q(medical_claim__claim_status__id=1) & Q(medical_claim__claim_year=current_year))).annotate(pending_amount=Sum('medical_claim__amount', filter=Q(medical_claim__claim_status__id=1) & Q(medical_claim__claim_year=current_year))).annotate(approved_amount=Sum('medical_claim__amount', filter=Q(medical_claim__claim_status__id=2) & Q(medical_claim__claim_year=current_year))).order_by('-pending_claims')

    yearly_limit = YEARLY_LIMIT

    claim_balance_by_user = {}

    for claim in pending_claims_by_user:
        username = claim['username']  # Accessing dictionary keys with string literals
        user_pending_amount = claim['pending_amount'] if claim['pending_amount'] is not None else 0
        user_approved_amount = claim['approved_amount'] if claim['approved_amount'] is not None else 0
        claim_balance_by_user[username] = yearly_limit - user_pending_amount - user_approved_amount

    context = {
        'admin_view': True,
        'pending_claims_by_user': pending_claims_by_user,
        'claim_balance_by_user': claim_balance_by_user,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount,
    }

    return render(request, 'mitasa_admin/medical_dashboard.html', context)

def history_table(request, year):
    claims = Claim.objects.filter(claim_year=year)
    approved_claims = claims.filter(claim_status__status="Approved")

    approved_claims_count = approved_claims.count()

    total_approved_amount = approved_claims.aggregate(Sum('approved_claim__amount'))['approved_claim__amount__sum'] or 0

    context = {
        "claims": claims,
        "year": year,

        "approved_claims_count": approved_claims_count,
        "total_approved_amount": total_approved_amount
    }

    return render(request, "history_table.html", context)