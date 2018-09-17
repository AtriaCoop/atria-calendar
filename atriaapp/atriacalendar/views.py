from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import CalendarItem


def index(request):
    latest_item_list = CalendarItem.objects.order_by('-pub_date')[:5]
    context = {'latest_item_list': latest_item_list}
    return render(request, 'calendar/index.html', context)

def detail(request, item_id):
    item = get_object_or_404(CalendarItem, pk=item_id)
    return render(request, 'calendar/detail.html', {'item': item})

def content(request, item_id):
    response = "You're looking at the content of item %s."
    return HttpResponse(response % item_id)

def translate(request, item_id):
    return HttpResponse("You're translating on item %s." % item_id)
