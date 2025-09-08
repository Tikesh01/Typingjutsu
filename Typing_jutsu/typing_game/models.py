from django.db import models

class user(models.Model):
    id=models.AutoField(primary_key=True, unique=True,)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=40, unique=True)
    mobile_num = models.BigIntegerField(max_length=10)
    role = models.CharField(max_length=10)
    password = models.CharField(max_length=8)
