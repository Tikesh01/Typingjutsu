from django.urls import path
from . import views

app_name = 'typing_game'

urlpatterns = [
    # Add your URL patterns here
    path('', views.signup, name='index'),  # This will be the main page for the typing game
]
