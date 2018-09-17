from django.contrib import admin

from .models import CalendarItem, ItemSchedule, ItemContent

admin.site.register(CalendarItem)
admin.site.register(ItemSchedule)
admin.site.register(ItemContent)
