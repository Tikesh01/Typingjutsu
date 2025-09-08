from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import user

def signup(request):
    if request.method == 'POST':
        try:
            # Get form data
            role = request.POST.get('role')
            name = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            mobile_num = request.POST.get('mobile_num')

            # Validate required fields
            if not all([role, name, email, password, confirm_password]):
                messages.error(request, 'All fields are required')
                return render(request, 'typing_game/signup.html')

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Invalid email format')
                return render(request, 'typing_game/signup.html')

            # Check if email already exists
            if user.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
                return render(request, 'typing_game/signup.html')

            # Validate password
            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return render(request, 'typing_game/signup.html')

            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return render(request, 'typing_game/signup.html')

            # Validate mobile number
            if mobile_num and (not mobile_num.isdigit() or len(mobile_num) != 10):
                messages.error(request, 'Invalid mobile number')
                return render(request, 'typing_game/signup.html')

            # Create new user
            new_user = user(
                name=name,
                email=email,
                mobile_num=mobile_num,
                role=role
            )
            new_user.set_password(password)
            new_user.save()

            messages.success(request, 'Account created successfully! Please login.')
            return redirect('typing_game:login')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'typing_game/signup.html')

    return render(request, 'typing_game/signup.html')

def login_view(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not email or not password:
                messages.error(request, 'Please provide both email and password')
                return render(request, 'typing_game/login.html')

            try:
                user_obj = user.objects.get(email=email)
            except user.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'typing_game/login.html')

            if user_obj.check_password(password):
                request.session['user_id'] = user_obj.id
                request.session['user_role'] = user_obj.role
                messages.success(request, f'Welcome back, {user_obj.name}!')
                return redirect('typing_game:home')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'typing_game/login.html')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'typing_game/login.html')

    return render(request, 'typing_game/login.html')

def logout_view(request):
    logout(request)
    return redirect('typing_game:home')

def home(request):
    return render(request, 'typing_game/home.html')

@login_required
def practice(request):
    return render(request, 'typing_game/practice.html')

@login_required
def competitions(request):
    return render(request, 'typing_game/competitions.html')

@login_required
def leaderboard(request):
    return render(request, 'typing_game/leaderboard.html')

@login_required
def profile(request):
    return render(request, 'typing_game/profile.html')

def about(request):
    return render(request, 'typing_game/about.html')

def contact(request):
    return render(request, 'typing_game/contact.html')

def terms(request):
    return render(request, 'typing_game/terms.html')

def privacy(request):
    return render(request, 'typing_game/privacy.html')

def help_view(request):
    return render(request, 'typing_game/help.html')
