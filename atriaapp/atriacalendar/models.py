from django.db import models


class CalendarItem(models.Model):
    item_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
            return self.item_name

class ItemSchedule(models.Model):
    calendar_item = models.ForeignKey(CalendarItem, on_delete=models.CASCADE)
    schedule_description = models.CharField(max_length=200)
    item_start_date = models.DateTimeField('start date/time')
    item_end_date = models.DateTimeField('end date/time')

    def __str__(self):
            return self.schedule_description

class ItemContent(models.Model):
    calendar_item = models.ForeignKey(CalendarItem, on_delete=models.CASCADE)
    language_cd = models.CharField(max_length=2)
    field_name = models.CharField(max_length=200)
    field_value = models.CharField(max_length=200)

    def __str__(self):
            return self.language_cd + ":" + self.field_name + "=" + self.field_value
