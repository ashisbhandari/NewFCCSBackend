from django.db import models
from users.models import User

# Create your models here.

class Manifest(models.Model):
    manifest_no = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cnNumbers = models.TextField()  # Store CN numbers as a comma-separated string
    status = models.CharField(max_length=50, default='Pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    manual_cn = models.TextField(blank=True, null=True)
    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    destination = models.TextField(blank=True, null=True)
    

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
    