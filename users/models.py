from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, email, ownerName, companyName, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, ownerName=ownerName, companyName=companyName, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, ownerName, companyName, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, ownerName, companyName, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    userID = models.CharField(max_length=20, editable=False, unique=True)
    companyName = models.CharField(max_length=255)
    ownerName = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    contact1 = models.CharField(max_length=20)
    contact2 = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    password = models.CharField(max_length=128)  # hashed by AbstractBaseUser
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['ownerName', 'companyName']

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # Auto-generate userID if not provided
        if not self.userID:
            count = User.objects.count() + 1
            self.userID = f'FCCS{count+1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ownerName} ({self.email})"
