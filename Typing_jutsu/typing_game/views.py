from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

def signup(request):
    return render(request, 'typing_game/signup.html')

def login_view(request):
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
