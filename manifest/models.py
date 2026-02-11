from django.db import models
from users.models import User

# Create your models here.

class Manifest(models.Model):
    manifest_no = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cnNumbers = models.TextField()  # Store CN numbers as a comma-separated string
    status = models.CharField(max_length=50, default='Pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # User's name
    contact_number = models.CharField(max_length=20, blank=True, null=True)  # User's contact number
    location = models.TextField(blank=True, null=True)  # User's location (auto-fetched from device)
    device_info = models.TextField(blank=True, null=True)  # Device info (type, OS, browser)
    ip_address = models.CharField(max_length=50, blank=True, null=True)  # Client IP address
    latitude = models.FloatField(blank=True, null=True)  # Latitude from GPS
    longitude = models.FloatField(blank=True, null=True)  # Longitude from GPS
    updated_at = models.DateTimeField(auto_now=True)  # Track last update
    

    def __str__(self):
        return str(self.id)
    
    class Meta:
        db_table = 'manifest'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.manifest_no = f"FCCS-MN{self.id}"
            super().save(update_fields=['manifest_no'])
    