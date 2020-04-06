from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

from .forms import *
from .models import *


def home(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # data extraction
            activity = form.cleaned_data.get('activity')
            vehicle = form.cleaned_data.get('vehicle')
            day = form.cleaned_data.get('day')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')

            # initial query for activity and vehicle
            existing_bookings = (b.dock_activity.id for b in Booking.objects.all())
            ac_ve_query = DockActivity.objects\
                .exclude(id__in=existing_bookings)\
                .filter(dock__category=vehicle,
                        activity=activity)

            # if start time is introduced, we'll show all the segments greater or equal to that one
            # TODO: Complete this

            context = {
                'form': form,
                'activities': ac_ve_query,
                'title': 'Search',
            }

            return render(request, 'dock_scheduler/home.html', context)
    else:
        existing_bookings = (b.dock_activity.id for b in Booking.objects.all())
        activities = DockActivity.objects.exclude(id__in=existing_bookings)
        form = SearchForm()
        context = {
            'form': form,
            'activities': activities,
            'title': 'Home',
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
                s = ', '
                message = s.join(message)
                message = message.lower().capitalize() + '.'
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


# @staff_member_required()
# def bookings(request):
#     context = {
#         'bookings': Booking.objects.all(),
#         'title': 'Bookings'
#     }
#     return render(request, 'dock_scheduler/.html', context)


def mybookings(request):
    if request.method == 'POST':
        form = BookingManagement(request.POST)
        if form.is_valid():
            driver = form.cleaned_data.get('driver')
            order = form.cleaned_data.get('order')
            reservation = Booking.objects.filter(driver=driver, order__pk=order)

            context = {
                'form': form,
                'bookings': reservation,
                'title': 'My bookings',
            }
            return render(request, 'dock_scheduler/myreservations.html', context)
    else:
        context = {
            'form': BookingManagement(),
            'bookings': None,
            'title': 'My bookings',
        }
        return render(request, 'dock_scheduler/myreservations.html', context)


def scheduleupload(request):
    context = {
        'form': DailySchedule(),
        'title': 'Schedule',
    }
    return render(request, 'dock_scheduler/scheduleform.html', context)


class ActivityDetailView(DetailView):
    model = DockActivity

    def get_context_data(self, **kwargs):
        context = super(ActivityDetailView, self).get_context_data(**kwargs)
        context['form'] = BookingForm()
        return context


class BookingFormView(FormView):
    form = BookingForm()
    success_url = ''
