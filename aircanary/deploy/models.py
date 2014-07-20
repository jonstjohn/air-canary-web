from django.db import models

class Push(models.Model):

    branch = models.CharField(max_length=200)
    tag = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
