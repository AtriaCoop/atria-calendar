from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)

admin.site.register(AtriaEventProgram)
admin.site.register(AtriaEvent)
admin.site.register(AtriaCalendar)
admin.site.register(AtriaOrganization)
admin.site.register(AtriaOrgAnnouncement)
admin.site.register(RelationType)
admin.site.register(AtriaRelationship)
admin.site.register(EventAttendanceType)
admin.site.register(AtriaBookmark)
admin.site.register(AtriaEventAttendance)
