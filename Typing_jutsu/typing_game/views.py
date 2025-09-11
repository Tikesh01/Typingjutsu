from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Participant, Organizer, Competition, CompetitionResult
from .decorators import login_required, participant_required, organizer_required
from django.utils import timezone


def get_auth_context(request):
    """Helper to get user auth context from session."""
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    return {
        'is_authenticated': bool(user_id),
        'user_role': user_role,
        'user_id' : user_id,
    }


def signup(request):
    if request.method == 'POST':
        try:
            # Get basic form data
            role = request.POST.get('role')
            name = request.POST.get('username')
            password = request.POST.get('password')

            # Basic validation for all users
            if not all([role, name, password]):
                messages.error(request, 'All fields are required')
                return render(request, 'typing_game/signup.html', get_auth_context(request))
            
            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return render(request, 'typing_game/signup.html', get_auth_context(request))
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
                        return render(request, 'typing_game/signup.html', get_auth_context(request))
                
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
                    return render(request, 'typing_game/signup.html', get_auth_context(request))
            
                if not all([email, mobile_num]):
                    messages.error(request, 'Email and mobile number are required for organizers')
                    return render(request, 'typing_game/signup.html', get_auth_context(request))

                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, 'Invalid email format')
                    return render(request, 'typing_game/signup.html', get_auth_context(request))

                if Organizer.objects.filter(email=email).exists():
                    messages.error(request, 'Email already registered')
                    return render(request, 'typing_game/signup.html', get_auth_context(request))

                if not mobile_num.isdigit() or len(mobile_num) != 10:
                    messages.error(request, 'Invalid mobile number')
                    return render(request, 'typing_game/signup.html', get_auth_context(request))

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
            return render(request, 'typing_game/signup.html', get_auth_context(request))

    return render(request, 'typing_game/signup.html', get_auth_context(request))

def login_view(request):
    if request.method == 'POST':
        try:
            identifier = request.POST.get('username') # This is 'username' or 'email'
            password = request.POST.get('password')

            if not identifier or not password:
                messages.error(request, 'Please provide both username/email and password')
                return render(request, 'typing_game/login.html', get_auth_context(request))

            user_obj = None
            user_role = None
            is_email = '@' in identifier

            if is_email:
                # Search only in Organizer table for email
                try:
                    user_obj = Organizer.objects.get(email=identifier)
                    user_role = 'organizer'
                except Organizer.DoesNotExist:
                    messages.error(request, 'No organizer found with this email.')
                    return render(request, 'typing_game/login.html', get_auth_context(request))
            else:
                # Search in Participant table first, then Organizer for username
                try:
                    user_obj = Participant.objects.get(name=identifier)
                    user_role = 'participant'
                except Participant.DoesNotExist:
                    try:
                        user_obj = Organizer.objects.get(name=identifier)
                        user_role = 'organizer'
                    except Organizer.DoesNotExist:
                        messages.error(request, 'No user found with this username.')
                        return render(request, 'typing_game/login.html', get_auth_context(request))

            if user_obj and user_obj.check_password(password):
                request.session['user_id'] = user_obj.id
                request.session['user_role'] = user_role
                request.session['user_name'] = user_obj.name
                request.session.set_expiry(0)  # Expire session on browser close
                messages.success(request, f'Welcome back, {user_obj.name}!')
                return redirect('typing_game:home')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
                return render(request, 'typing_game/login.html', get_auth_context(request))
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return render(request, 'typing_game/login.html', get_auth_context(request))

    return render(request, 'typing_game/login.html', get_auth_context(request))

def logout_view(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('typing_game:home')

def home(request):
    context = get_auth_context(request)
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role') # This line was missing
    profile_user = None

    if user_id and user_role:
        try:
            if user_role == 'participant':
                profile_user = Participant.objects.get(id=user_id)
            elif user_role == 'organizer':
                profile_user = Organizer.objects.get(id=user_id)
        except (Participant.DoesNotExist, Organizer.DoesNotExist):
            # If user in session doesn't exist in DB, clear session
            request.session.flush()

    context['profile_user'] = profile_user
    return render(request, 'typing_game/home.html', context)

@participant_required
def practice(request):
    """Practice page - only accessible to participants"""
    return render(request, 'typing_game/practice.html', get_auth_context(request))

@login_required
def competitions(request):
    context = get_auth_context(request)
    user_role = context['user_role']
    user_id = context['user_id']

    all_comps = Competition.objects.all().order_by('start_time')
    # keep only active/upcoming competitions
    competitions_list = [c for c in all_comps if c.end_time >= timezone.now()]

    if user_role == 'organizer':
        organizer_comps = Competition.objects.filter(organizer_id=user_id).order_by('start_time')
        # add organizer's expired ones also
        competitions_list = list(set(list(competitions_list) + list(organizer_comps)))
        competitions_list.sort(key=lambda x: x.start_time)

    for comp in competitions_list:
        # Check if competition is active: started and within time frame
        comp.is_active = comp.started and comp.start_time <= timezone.now() < comp.end_time
        comp.expired = True if comp.end_time < timezone.now() else False

    if user_role == 'participant':
        participant = Participant.objects.get(id=user_id)
        for comp in competitions_list:
            comp.is_joined = comp.participants.filter(id=participant.id).exists()

    context['competitions'] = competitions_list
    return render(request, 'typing_game/competitions.html', context)

@organizer_required
def create_competition(request):
    """Allows organizers to create a new competition."""
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            competition_type = request.POST.get('type')
            description = request.POST.get('description')
            paragraphs_raw = request.POST.get('paragraphs')
            start_time = request.POST.get('start_time')
            duration = request.POST.get('duration')
            organizer_id = request.session.get('user_id')

            if not all([title, competition_type, description, start_time, duration,paragraphs_raw]):
                messages.error(request, "All fields are required.")
                return render(request, 'typing_game/create_competition.html', get_auth_context(request))

            paragraphs_list = [p.strip() for p in paragraphs_raw.split('\n\n') if p.strip()]
            
            # Prepare data for JSONField
            paragraphs_data = []
            if competition_type == 'Jumble-words':
                answers_raw = request.POST.get('ans_juble_word', '')
                answers_list = [a.strip() for a in answers_raw.split('\n') if a.strip()]
                if len(paragraphs_list) != len(answers_list):
                    messages.error(request, "The number of jumbled words must match the number of answers.")
                    return render(request, 'typing_game/create_competition.html', get_auth_context(request))
                
                for jumbled, answer in zip(paragraphs_list, answers_list):
                    paragraphs_data.append({'jumbled': jumbled, 'answer': answer})
            else:
                for para in paragraphs_list:
                    paragraphs_data.append({'text': para})

            organizer = Organizer.objects.get(id=organizer_id)
            Competition.objects.create(
                title=title,
                description=description,
                type=competition_type,
                paragraphs=paragraphs_data,
                start_time=start_time,
                duration=int(duration),
                organizer=organizer
            )
            messages.success(request, f"Competition '{title}' created successfully!")
            return redirect('typing_game:competitions')
        except Exception as e:
            messages.error(request, f"An error occurred while creating the competition: {e}")
            return render(request, 'typing_game/create_competition.html', get_auth_context(request))

    return render(request, 'typing_game/create_competition.html', get_auth_context(request))

@organizer_required
def edit_competition(request, competition_id):
    """Allows organizers to edit their own competitions."""
    competition = get_object_or_404(Competition, id=competition_id, organizer_id=request.session.get('user_id'))

    if request.method == 'POST':
        try:
            # Update competition fields based on form data
            competition.title = request.POST.get('title')
            competition.description = request.POST.get('description')
            competition.type = request.POST.get('type')
            competition.start_time = request.POST.get('start_time')
            competition.duration = request.POST.get('duration')            

            paragraphs_raw = request.POST.get('paragraphs')
            paragraphs_list = [p.strip() for p in paragraphs_raw.split('\n\n') if p.strip()]

            competition.paragraphs = [{'text': para} for para in paragraphs_list]

            competition.save()
            messages.success(request, f"Competition '{competition.title}' updated successfully!")
            return redirect('typing_game:competitions')
        except Exception as e:
            messages.error(request, f"An error occurred while updating the competition: {e}")
            return render(request, 'typing_game/edit_competition.html', {'competition': competition})

    return render(request, 'typing_game/edit_competition.html', {'competition': competition})

@organizer_required
def delete_competition(request, competition_id):
    """Allows organizers to delete their own competitions."""
    try:
        competition = Competition.objects.get(id=competition_id, organizer_id=request.session.get('user_id'))
        competition.delete()
        messages.success(request, "Competition deleted successfully!")
    except Competition.DoesNotExist:
        messages.error(request, "Competition not found or you don't have permission to delete it.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the competition: {e}")
    return redirect('typing_game:competitions')

# Update the start_competition view to redirect to live competition
@organizer_required
def start_competition(request, competition_id):
    """Allows organizers to start their own competitions and redirect to live view."""
    try:
        competition = Competition.objects.get(id=competition_id, organizer_id=request.session.get('user_id'))
        competition.started = True
        competition.save()
        messages.success(request, f"Competition '{competition.title}' started successfully!")
        return redirect('typing_game:live_competition', competition_id=competition_id)
    except Competition.DoesNotExist:
        messages.error(request, "Competition not found or you don't have permission to start it.")
    except Exception as e:
        messages.error(request, f"An error occurred while starting the competition: {e}")
    return redirect('typing_game:competitions')

@participant_required
def join_competition(request, competition_id):
    participant = Participant.objects.get(id=request.session.get('user_id'))
    competition = Competition.objects.get(id=competition_id)
    
    # Check if the competition has already started
    if competition.started and competition.start_time <= timezone.now():
        # Add participant and redirect to live competition
        competition.participants.add(participant)
        messages.success(request, f"You have successfully joined the '{competition.title}' competition!")
        return redirect('typing_game:live_competition', competition_id=competition_id)
    else:
        competition.participants.add(participant)
        messages.success(request, f"You have successfully joined the '{competition.title}' competition! It will start at {competition.start_time}.")
        return redirect('typing_game:competitions')


# Add to views.py
@login_required
def live_competition(request, competition_id):
    """Live competition page with different views for participants and organizers"""
    competition = get_object_or_404(Competition, id=competition_id)
    user_role = request.session.get('user_role')
    user_id = request.session.get('user_id')
    context = get_auth_context(request)
    context['competition'] = competition
    
    # Check if competition has started
    if not competition.started and user_role == 'participant':
        messages.error(request, "This competition hasn't started yet.")
        return redirect('typing_game:competitions')
    
    # Check if competition has expired
    if competition.end_time < timezone.now():
        messages.error(request, "This competition has ended.")
        return redirect('typing_game:competitions')
    
    # For participants, check if they've joined
    if user_role == 'participant':
        participant = Participant.objects.get(id=user_id)
        if not competition.participants.filter(id=participant.id).exists():
            messages.error(request, "You need to join this competition first.")
            return redirect('typing_game:competitions')
    
    # Calculate time remaining
    time_remaining = competition.end_time - timezone.now()
    context['time_remaining_seconds'] = max(0, time_remaining.total_seconds())
    
    # For organizers, get all results
    if user_role == 'organizer':
        # Get all participants who have submitted results
        results = CompetitionResult.objects.filter(competition=competition).select_related('participant')
        
        # Calculate scores based on competition type
        for result in results:
            if competition.type in ['Normal', 'Reverse']:
                result.score = (result.wpm * result.accuracy) / 100
            elif competition.type == 'Jumble-Word':
                # For jumble word, use accuracy as primary metric
                result.score = result.accuracy
        
        # Sort results by score (descending)
        results = sorted(results, key=lambda x: x.score, reverse=True)
        context['results'] = results
    
    return render(request, 'typing_game/live_competition.html', context)


@participant_required
def submit_result(request, competition_id):
    """Handle submission of typing results from participants"""
    if request.method == 'POST':
        try:
            competition = get_object_or_404(Competition, id=competition_id)
            participant = Participant.objects.get(id=request.session.get('user_id'))
            
            # Check if competition is still active
            if competition.end_time < timezone.now():
                return JsonResponse({'error': 'Competition has ended'}, status=400)
            
            # Get data from request
            wpm = float(request.POST.get('wpm', 0))
            accuracy = float(request.POST.get('accuracy', 0))
            time_taken = float(request.POST.get('time_taken', 0))
            total_keystrokes = int(request.POST.get('total_keystrokes', 0))
            correct_keystrokes = int(request.POST.get('correct_keystrokes', 0))
            
            # Create or update result
            result, created = CompetitionResult.objects.update_or_create(
                competition=competition,
                participant=participant,
                defaults={
                    'wpm': wpm,
                    'accuracy': accuracy,
                    'time_taken': time_taken,
                    'total_keystrokes': total_keystrokes,
                    'correct_keystrokes': correct_keystrokes,
                    'submitted_at': timezone.now()
                }
            )
            
            return JsonResponse({'success': True, 'message': 'Result submitted successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def leaderboard(request):
    """Leaderboard page - accessible to all logged-in users"""
    return render(request, 'typing_game/leaderboard.html', get_auth_context(request))

# Public pages
def terms(request):
    """Terms of service page"""
    return render(request, 'typing_game/terms.html', get_auth_context(request))

def privacy(request):
    """Privacy policy page"""
    return render(request, 'typing_game/privacy.html', get_auth_context(request))

def help_view(request):
    """Help page"""
    return render(request, 'typing_game/help.html', get_auth_context(request))

def health_check(request):
    """Health check endpoint for Render."""
    return HttpResponse("OK", status=200)
