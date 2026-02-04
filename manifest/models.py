from django.db import models

# Create your models here.

class Manifest(models.Model):
    manifest_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cnNumbers = models.TextField()  # Store CN numbers as a comma-separated string
    

    def __str__(self):
        return self.manifest_id
    