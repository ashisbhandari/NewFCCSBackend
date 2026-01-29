from django.db import models

# Create your models here.

# add users table
class User(models.Model):
    id = models.AutoField(primary_key=True)
    userID = models.CharField(max_length=20, editable=False, unique=True)
    companyName = models.CharField(max_length=255)
    ownerName = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100)
    Zipcode = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    contact1 = models.CharField(max_length=20)
    contact2 = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128, default='') 

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # Auto-generate userID if not provided
        if not self.userID:
            count = User.objects.count()
            self.userID = f'FCCS{count + 1}'  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ownerName
