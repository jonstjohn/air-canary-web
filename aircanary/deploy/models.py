from django.db import models

class Push(models.Model):
    """ A push to the repository """
    branch = models.CharField(max_length=200)
    tag = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

class Deploy(models.Model):
    """ A deploy of code """
    ref = models.CharField(max_length=200)
    rev = models.CharField(max_length=40)
    success = models.BooleanField(default=False)
    output = models.TextField(blank=True, null=True)
    deployed = models.DateTimeField(auto_now_add=True)
