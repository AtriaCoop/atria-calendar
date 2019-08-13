from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from swingtime.models import Occurrence

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


class AtriaOrganizationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            action = "change"
        else:
            action = "add"
        super().save_model(request, obj, form, change)
        if not change:
            # add a default calendar for the organization
            calendar = AtriaCalendar(org_owner=obj, calendar_name='Events')
            calendar.save()


admin.site.register(AtriaEventProgram)
admin.site.register(AtriaEvent)
admin.site.register(Occurrence)
admin.site.register(AtriaCalendar)
admin.site.register(AtriaOrganization, AtriaOrganizationAdmin)
admin.site.register(AtriaOrgAnnouncement)
admin.site.register(RelationType)
admin.site.register(AtriaRelationship)
admin.site.register(EventAttendanceType)
admin.site.register(AtriaBookmark)
admin.site.register(AtriaEventAttendance)
admin.site.register(AtriaOccurrence)
