from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Participant(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=128, unique=True)
    created_At = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'participants'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"Participant: {self.name}"


class Organizer(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=40, unique=True)
    mobile_num = models.CharField(max_length=10)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'organizers'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"Organizer: {self.name} ({self.email})"
    
class Competition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='competitions')
    participants = models.ManyToManyField(Participant, related_name='competitions', blank=True)
    type =

    def __str__(self):
        return self.title