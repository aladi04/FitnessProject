from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member, Admin

class CustomUserAdmin(UserAdmin):
    model = Member
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'age', 'gender', 'height', 'weight')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'first_name', 'last_name')}),
    )

admin.site.register(Member, CustomUserAdmin)
admin.site.register(Admin)