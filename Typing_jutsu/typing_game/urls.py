from django.urls import path
from . import views

app_name = 'typing_game'

urlpatterns = [
    path('', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main navigation URLs
    path('home/', views.home, name='home'),
    path('practice/', views.practice, name='practice'),
    path('competitions/', views.competitions, name='competitions'),
    path('competitions/create/', views.create_competition, name='create_competition'),
    path('competitions/<int:competition_id>/join/', views.join_competition, name='join_competition'),
    path('competitions/edit/<int:competition_id>/', views.edit_competition, name='edit_competition'),
    path('competitions/delete/<int:competition_id>/', views.delete_competition, name='delete_competition'),
    path('competition/<int:competition_id>/start-now/', views.start_competition_now, name='start_competition_now'),
    path('competition/<int:competition_id>/status/', views.update_competition_status, name='update_competition_status'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('competition/<int:competition_id>/live/', views.live_competition, name='live_competition'),
    path('competition/<int:competition_id>/submit/', views.submit_result, name='submit_result'),
    
    # Footer URLs
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('help/', views.help_view, name='help'),

    # Health check for deployment platforms
    path('health_check/', views.health_check, name='health_check'),
]
