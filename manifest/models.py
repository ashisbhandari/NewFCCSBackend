from django.db import models
from users.models import User

# Create your models here.

class Manifest(models.Model):
    manifest_id = models.CharField(max_length=100, unique=True, blank=True)
    manifest_no = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cnNumbers = models.TextField()  # Store CN numbers as a comma-separated string
    status = models.CharField(max_length=50,default='Pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return self.manifest_id
    
    class Meta:
        db_table = 'manifest'

    def save(self, *args, **kwargs):
        if self.manifest_id:
            self.manifest_no = f"FCCS-MN{self.manifest_id}"
        super().save(*args, **kwargs)
    