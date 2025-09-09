from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Participant, Organizer

def signup(request):
    if request.method == 'POST':
        try:
            # Get basic form data
            role = request.POST.get('role')
            name = request.POST.get('username')
            password = request.POST.get('password')

            # Basic validation for all users
            if not all([role, name, password]):
                messages.error(request, 'Name and password are required')
                return render(request, 'typing_game/signup.html')


            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return render(request, 'typing_game/signup.html')
            if role == 'participant':
                # Simple registration for participants
                new_user = Participant(
                    name=name,
                )
                new_user.set_password(password)
                
                # Check if this password is already used by comparing hashes
                existing_participants = Participant.objects.all()
                for participant in existing_participants:
                    if participant.check_password(password):
                        messages.error(request, 'This password is already used by another participant. Please choose a different password.')
                        return render(request, 'typing_game/signup.html')
                
                new_user.save()
                messages.success(request, 'Welcome to Typing Jutsu! Please login to start practicing.')
                
            elif role == 'organizer':
                # Get additional data for organizers
                email = request.POST.get('email')
                mobile_num = request.POST.get('mobile_num')
                confirm_password = request.POST.get('confirm_password')
                
                # Additional validation for organizers
                if (password != confirm_password) and confirm_password != None:
                    messages.error(request, 'Passwords do not match')
                    return render(request, 'typing_game/signup.html')
            
                if not all([email, mobile_num]):
                    messages.error(request, 'Email and mobile number are required for organizers')
                    return render(request, 'typing_game/signup.html')

                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, 'Invalid email format')
                    return render(request, 'typing_game/signup.html')

                if Organizer.objects.filter(email=email).exists():
                    messages.error(request, 'Email already registered')
                    return render(request, 'typing_game/signup.html')

                if not mobile_num.isdigit() or len(mobile_num) != 10:
                    messages.error(request, 'Invalid mobile number')
                    return render(request, 'typing_game/signup.html')

                new_user = Organizer(
                    name=name,
                    email=email,
                    mobile_num=mobile_num,
                )
                new_user.set_password(password)
                new_user.save()
                messages.success(request, 'Organizer account created successfully! Please login.')

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
