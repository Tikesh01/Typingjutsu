from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('typing_game.urls')),  # This makes the typing game available at the root URL
]
