from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class user(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=40, unique=True)
    mobile_num = models.CharField(max_length=10)  # Changed to CharField as BigInteger doesn't support max_length
    role = models.CharField(max_length=20, choices=[('participant', 'Participant'), ('organizer', 'Organizer')])
    password = models.CharField(max_length=128)  # Increased for hashed password
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
class organizer(user):
    def __str__(self):
        return self.__dict__
    
class participant(user):
    
    def __str__(self):
        return self.__dict__