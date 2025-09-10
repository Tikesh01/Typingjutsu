from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('typing_game:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def participant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is logged in and is a participant
        if 'user_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('typing_game:login')
        if request.session.get('user_role') != 'participant':
            messages.error(request, 'This page is only accessible to participants.')
            return redirect('typing_game:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def organizer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is logged in and is an organizer
        if 'user_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('typing_game:login')
        if request.session.get('user_role') != 'organizer':
            messages.error(request, 'This page is only accessible to organizers.')
            return redirect('typing_game:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
