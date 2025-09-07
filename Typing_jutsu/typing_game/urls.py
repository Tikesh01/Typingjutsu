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
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('profile/', views.profile, name='profile'),
    
    # Footer URLs
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('help/', views.help_view, name='help'),
]
