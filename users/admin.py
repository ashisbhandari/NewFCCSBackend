from django.contrib import admin
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('ownerName', 'email', 'companyName', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'country', 'date_joined')
    search_fields = ('ownerName', 'email', 'companyName')
    readonly_fields = ('date_joined',)
    fieldsets = (
        ('Company Information', {
            'fields': ('companyName', 'ownerName')
        }),
        ('Contact Information', {
            'fields': ('email', 'contact1', 'contact2')
        }),
        ('Address', {
            'fields': ('address1', 'address2', 'city', 'state', 'country', 'Zipcode')
        }),
        ('Permissions', {
            'fields': ('is_staff',)
        }),
        ('Important Dates', {
            'fields': ('date_joined',)
        }),
    )
