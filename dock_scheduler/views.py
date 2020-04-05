from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import BookingForm
from .models import *

docks = [
    {
        'id': '0',
        'driver': '4213KFN',
        'order': '144326',
        'type': 'Large',
        'status': 'Booked'
    },
    {
        'id': '1',
        'driver': '5619HYI',
        'order': '997351',
        'type': 'Large',
        'status': 'Free'
    },
]


def home(request):
    context = {
        'docks': docks
    }
    return render(request, 'dock_scheduler/home.html', context)


def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # data extraction
            dock_number = form.cleaned_data.get('dock_number')
            day = form.cleaned_data.get('day')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            activity = form.cleaned_data.get('activity')
            order = form.cleaned_data.get('order')
            driver = form.cleaned_data.get('driver')

            # checking for availability and errors
            error_message = 'The following problems were detected: <br>'
            message = []
            # invalid order number
            if len(Order.objects.filter(number=order)) == 0:
                message.append('No order associated to that number')
            # invalid dock number
            if len(Dock.objects.filter(number=dock_number)) == 0:
                message.append("The dock solicited doesn't exist")
            # no time segment corresponding to the one solicited
            ts_query = TimeSegment.objects.filter(dock__number=dock_number,
                                                  day=day,
                                                  start_time=start_time,
                                                  end_time=end_time,
                                                  activity=activity)
            if len(ts_query) == 0:
                message.append('Zero matching time segments')

            # time segment already booked
            if len(Booking.objects.filter(time_segment=ts_query.first())):
                message.append('Time segment already booked')

            # if errors have been detected
            if len(message) != 0:
                s = '<br>'
                message = s.join(message)
                messages.error(request, message)

            # if there were no errors within the form
            else:
                new_booking = Booking(time_segment=ts_query.first(), driver=driver)
                new_booking.save()
                messages.success(request, 'Booked!')
                return redirect('scheduler-home')

    else:
        form = BookingForm()
        return render(request, 'dock_scheduler/book.html', {'form': form, 'title': 'Booking'})
