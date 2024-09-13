from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserForm, ProfileForm
from django.contrib.auth.forms import PasswordChangeForm

# View Functions
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.user.is_staff:
                return redirect("index")
            else:
                return redirect("index")
    else:
        form = AuthenticationForm()

    context = {
        'form': form
    }
    return render(request, 'user/login/login.html', context)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect("user:login")
    
@login_required(login_url='user:login')
def profile_view(request):
    context = {
        
    }  
    return render(request, 'user/profile/profile.html', context)

@login_required(login_url='user:login')
def profile_new(request):
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("user:profile")
    else:
        form = ProfileForm()

    context = {
        'form': form
    }
    return render(request, 'user/profile/profile_edit.html', context)

@login_required(login_url='user:login')
def user_edit(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user:profile")
    else:
        form = UserForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'user/profile/user_edit.html', context)

@login_required(login_url='user:login')
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user:profile")
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
    }
    return render(request, 'user/profile/profile_edit.html', context)

def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("user:profile")
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'user/profile/password_change.html', context)