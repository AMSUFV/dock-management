import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView, FormView

from .forms import *
from .models import *
from .utils.csv_parser import handle_file


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
            ac_ve_query = DockActivity.objects \
                .exclude(id__in=existing_bookings) \
                .filter(dock__category=vehicle,
                        activity=activity)

            if day is not None:
                ac_ve_query = ac_ve_query.filter(
                    time_segment__day=day
                )
            # if both times are supplied, we'll do an exact query
            if start_time is not None and end_time is not None:
                ac_ve_query = ac_ve_query.filter(
                    time_segment__start_time=start_time,
                    time_segment__end_time=end_time,
                )
            # if start time is introduced, we'll show all the segments greater or equal to that one
            elif start_time is not None:
                ac_ve_query = ac_ve_query.filter(
                    time_segment__start_time__gte=start_time,
                )
            # if end time is introduced, we'll show all the segments less than or equal to that one
            elif end_time is not None:
                ac_ve_query = ac_ve_query.filter(
                    time_segment__end_time__lte=end_time,
                )

            context = {
                'form': form,
                'activities': ac_ve_query,
                'title': 'Search',
            }

            return render(request, 'dock_scheduler/home.html', context)
        else:
            existing_bookings = (b.dock_activity.id for b in Booking.objects.all())
            activities = DockActivity.objects.exclude(id__in=existing_bookings)
            messages.warning(request, 'Check your form for mistakes')
            context = {
                'form': form,
                'activities': activities,
                'title': 'Search',
            }
            return render(request, 'dock_scheduler/home.html', context)

    else:
        existing_bookings = (b.dock_activity.id for b in Booking.objects.all())
        activities = DockActivity.objects.exclude(id__in=existing_bookings)\
            .filter(time_segment__day=datetime.date.today())
        form = SearchForm()
        context = {
            'form': form,
            'activities': activities,
            'title': 'Home',
        }
        return render(request, 'dock_scheduler/home.html', context)


# @staff_member_required()
# def bookings(request):
#     context = {
#         'bookings': Booking.objects.all(),
#         'title': 'Bookings'
#     }
#     return render(request, 'dock_scheduler/.html', context)


def mybookings(request):
    context = {
        'form': BookingManagement(),
        'title': 'My bookings',
    }
    if request.method == 'POST':
        form = BookingManagement(request.POST)
        if form.is_valid():
            driver = form.cleaned_data.get('driver')
            order = form.cleaned_data.get('order')
            reservation = Booking.objects.filter(driver=driver, order__pk=order)

            context = {
                'form': form,
                'bookings': reservation,
                'title': 'Results',
            }

            if len(reservation) == 0:
                messages.warning(request, 'No matching bookings')
                return render(request, 'dock_scheduler/myreservations.html', context)

            else:
                return render(request, 'dock_scheduler/myreservations.html', context)
        else:
            # if the form is not valid
            context['form'] = form
            context['title'] = 'Error'
            return render(request, 'dock_scheduler/myreservations.html', context)

    else:
        return render(request, 'dock_scheduler/myreservations.html', context)


def scheduleupload(request):
    context = {
        'form': DailySchedule(),
        'title': 'Schedule',
    }
    # get today's date and schedule
    today = datetime.date.today()
    segments = TimeSegment.objects.filter(day=today)
    today_activities = DockActivity.objects.filter(time_segment__day=today)
    docks = Dock.objects.filter(number__in=today_activities)

    daily_schedules = []
    for i, dock in enumerate(docks):
        activities = today_activities.filter(dock__number=dock.number)
        daily_schedule = [dock.number, dock.category]
        for activity in activities:
            daily_schedule.append(activity.activity)
        daily_schedules.append(daily_schedule)

    context['segments'] = segments
    context['daily_schedules'] = daily_schedules

    if request.method == 'POST':

        form = DailySchedule(request.POST, request.FILES)
        if form.is_valid():
            day = form.cleaned_data.get('day')
            handle_file(request.FILES['schedule'], day)

            messages.success(request, 'Schedule added!')

            return render(request, 'dock_scheduler/scheduleform.html', context)

        else:
            messages.warning(request, 'Check the form for errors')
            context['form'] = form
            return render(request, 'dock_scheduler/scheduleform.html', context)
    else:
        return render(request, 'dock_scheduler/scheduleform.html', context)


class ActivityDetailView(DetailView):
    model = DockActivity

    def get_context_data(self, **kwargs):
        context = super(ActivityDetailView, self).get_context_data(**kwargs)

        # populating the form
        current_activity = DockActivity.objects.filter(id=self.kwargs['pk']).first()
        form = BookingForm(initial={
            'vehicle': current_activity.dock.category,
            'activity': current_activity.activity,
            'dock_number': current_activity.dock.number,
            'day': current_activity.time_segment.day,
            'start_time': current_activity.time_segment.start_time,
            'end_time': current_activity.time_segment.end_time,
        })
        # hiding fields
        form.fields['vehicle'].widget = forms.HiddenInput()
        form.fields['activity'].widget = forms.HiddenInput()
        form.fields['dock_number'].widget = forms.HiddenInput()
        form.fields['day'].widget = forms.HiddenInput()
        form.fields['start_time'].widget = forms.HiddenInput()
        form.fields['end_time'].widget = forms.HiddenInput()

        context['form'] = form

        return context


class BookingFormView(FormView):
    form = BookingForm

    def form_valid(self, form):
        dock_number = form.cleaned_data.get('dock_number')
        day = form.cleaned_data.get('day')
        start_time = form.cleaned_data.get('start_time')
        end_time = form.cleaned_data.get('end_time')
        activity = form.cleaned_data.get('activity')
        order = form.cleaned_data.get('order')
        driver = form.cleaned_data.get('driver')

        ts_query = TimeSegment.objects.filter(dock__number=dock_number,
                                              day=day,
                                              start_time=start_time,
                                              end_time=end_time,
                                              activity=activity).first()

        new_booking = Booking(
            time_segment=ts_query,
            driver=driver,
            order=order)

        new_booking.save()


class DetailView(View):

    def get(self, request, *args, **kwargs):
        view = ActivityDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            dock_number = form.cleaned_data.get('dock_number')
            day = form.cleaned_data.get('day')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            activity = form.cleaned_data.get('activity')
            order = form.cleaned_data.get('order')
            driver = form.cleaned_data.get('driver')

            time_segment = TimeSegment.objects.filter(
                day=day,
                start_time=start_time,
                end_time=end_time
            ).first()

            dock_activity = DockActivity.objects.filter(
                dock__number=dock_number,
                time_segment=time_segment,
                activity=activity,
            ).first()

            order_query = Order.objects.filter(number=order)
            if len(order_query) > 0:
                order = order_query.first()
                # if there are no orders with that number already booked:
                if len(Booking.objects.filter(order=order)) == 0:
                    new_booking = Booking(
                        dock_activity=dock_activity,
                        order=order,
                        driver=driver,
                    )

                    messages.success(request, 'Booked!')
                    new_booking.save()

                    return redirect('scheduler-home')
                else:
                    messages.warning(request, 'Order already booked')
            else:
                messages.warning(request, 'Order not found')
            return redirect('activity-detail', pk=self.kwargs['pk'])
        else:
            messages.warning(request, 'Enter a valid order and license plate')
            return redirect('activity-detail', pk=self.kwargs['pk'])
