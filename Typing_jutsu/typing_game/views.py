from django.shortcuts import render, redirect, get_list_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Participant, Organizer, Competition
from .decorators import login_required, participant_required, organizer_required
from django.utils import timezone


def get_auth_context(request):
    """Helper to get user auth context from session."""
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    return {
        'is_authenticated': bool(user_id),
        'user_role': user_role,
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
    """
    Displays a list of competitions.
    - Organizers can see all competitions and a link to create new ones.
    - Participants can see upcoming competitions and join them.
    """
    context = get_auth_context(request)
    all_competitions = Competition.objects.filter(end_time__gte=timezone.now()).order_by('start_time') # Show started and upcoming

    if context['user_role'] == 'participant':
        user_id = request.session.get('user_id')
        participant = Participant.objects.get(id=user_id)
        # Annotate each competition with whether the participant has joined
        for comp in all_competitions:
            comp.is_joined = comp.participants.filter(id=participant.id).exists()

    context['competitions'] = all_competitions
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
            end_time = request.POST.get('end_time')
            organizer_id = request.session.get('user_id')

            if not all([title, competition_type, description, start_time, end_time,paragraphs_raw]):
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
                end_time=end_time,
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
            competition.end_time = request.POST.get('end_time')

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

@organizer_required
def start_competition(request, competition_id):
    """Allows organizers to start their own competitions."""
    try:
        competition = Competition.objects.get(id=competition_id, organizer_id=request.session.get('user_id'))
        competition.started = True
        competition.save()
        messages.success(request, f"Competition '{competition.title}' started successfully!")
    except Competition.DoesNotExist:
        messages.error(request, "Competition not found or you don't have permission to start it.")
    except Exception as e:
        messages.error(request, f"An error occurred while starting the competition: {e}")
    return redirect('typing_game:competitions')
@participant_required
def join_competition(request, competition_id):
    participant = Participant.objects.get(id=request.session.get('user_id'))
    competition = Competition.objects.get(id=competition_id)
    competition.participants.add(participant)
    messages.success(request, f"You have successfully joined the '{competition.title}' competition!")
    return redirect('typing_game:competitions')

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
