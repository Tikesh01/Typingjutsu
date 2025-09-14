from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone

class Participant(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
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
    description = models.JSONField(default=list)
    start_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes", default=3)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='competitions')
    participants = models.ManyToManyField(Participant, related_name='competitions',)
    type = models.CharField(
        max_length=15,
        choices=[('Normal','normal'), ('Reverse','reverse'), ('Jumble-Word','jumble-word')],
    )
    paragraphs = models.JSONField(default=list) 
    expired = models.BooleanField(default=False)
    started = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('waiting', 'Waiting'), ('active','Active'), ( 'ended','Ended')], default='waiting')

    @property
    def end_time(self):
        """Calculate end_time dynamically from start_time + duration"""
        return self.start_time + timedelta(minutes=self.duration)
    
    # In models.py, add to Competition class
    

    def __str__(self):
        return self.title

# Add to models.py
class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='competition_results')
    wpm = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    time_taken = models.FloatField(default=0.0)  # in seconds
    total_keystrokes = models.IntegerField(default=0)
    correct_keystrokes = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0) # For jumble-words
    total_questions = models.IntegerField(default=0) # For jumble-words
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0, editable=False)

    class Meta:
        db_table = 'competition_results'
        unique_together = ('competition', 'participant')

    def save(self, *args, **kwargs):
        # Only calculate score for typing-based games.
        # Jumble-word score is calculated on the client and saved directly.
        if self.competition.type in ['Normal', 'Reverse'] and self.accuracy > 0:
            self.score = self.wpm * (self.accuracy / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.participant.name} - {self.competition.title}"