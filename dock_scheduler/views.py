from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, DeleteView, ListView

from .forms import *
from .models import *
from .utils.csv_parser import handle_schedule, handle_orders


class HomeListView(ListView):
    model = DockActivity
    template_name = 'dock_scheduler/home.html'
    context_object_name = 'activities'
    ordering = ['time_segment__day', 'time_segment__start_time']
    paginate_by = 8

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        form = SearchForm()
        context['form'] = form

        return context

    def get_queryset(self, **kwargs):
        unavailable = DockActivity.objects.filter(activity='UA')
        existing_bookings = (b.dock_activity.id for b in Booking.objects.all())
        activities = DockActivity.objects \
            .exclude(id__in=existing_bookings) \
            .exclude(id__in=unavailable)

        activity = self.kwargs.get('activity')
        vehicle = self.kwargs.get('vehicle')
        day = self.kwargs.get('day')
        start_time = self.kwargs.get('start_time')
        end_time = self.kwargs.get('end_time')

        if vehicle != 'None' and activity != 'None':
            activities = activities.filter(dock__category=vehicle, activity=activity)

        if day != 'None':
            activities = activities.filter(time_segment__day=day)

        elif start_time != 'None' and end_time != 'None':
            activities = activities.filter(time_segment__start_time__gte=start_time)\
                                   .filter(time_segment__end_time__lte=end_time)
        elif start_time != 'None':
            activities = activities.filter(time_segment__start_time__gte=start_time)

        elif end_time != 'None':
            activities = activities.filter(time_segment__end_time__lte=end_time)

        activities = activities.order_by('time_segment__day').order_by('time_segment__start_time')

        return activities


class Home(View):

    def get(self, request, *args, **kwargs):
        view = HomeListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():

            return redirect('scheduler-search', **form.cleaned_data)
        else:
            unavailable = DockActivity.objects.filter(activity='UA')
            existing_bookings = (b.dock_activity.id for b in Booking.objects.all())

            activities = DockActivity.objects \
                .exclude(id__in=existing_bookings) \
                .exclude(id__in=unavailable)

            messages.warning(request, 'Check your form for mistakes')
            context = {
                'form': form,
                'activities': activities,
                'title': 'Search',
            }
            return render(request, 'dock_scheduler/home.html', context)


def home(request):
    unavailable = DockActivity.objects.filter(activity='UA')
    existing_bookings = (b.dock_activity.id for b in Booking.objects.all())

    activities = DockActivity.objects \
        .exclude(id__in=existing_bookings) \
        .exclude(id__in=unavailable)


@staff_member_required(login_url=reverse_lazy('login'))
def scheduleupload(request):

    context = {
        'form': DailySchedule(),
        'title': 'Schedule',
    }
    # get today's date and schedule
    today = datetime.date.today()
    segments = TimeSegment.objects.filter(day=today)
    today_activities = DockActivity.objects.filter(time_segment__day=today)
    numbers = today_activities.order_by().values_list('dock', flat=True).distinct()
    docks = Dock.objects.filter(number__in=numbers)

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
            day_activities = DockActivity.objects.filter(time_segment__day=day)

            if len(day_activities):
                messages.warning(request, 'A schedule for this day already exists.')
                return render(request, 'dock_scheduler/schedule_upload_form.html', context)

            try:
                handle_schedule(request.FILES['schedule'], day)
            except (ValueError, TypeError, IndexError):
                messages.warning(request, 'Something went wrong while handling your file. '
                                          'Make sure you have the right file and that no typos are present in it.')
                return render(request, 'dock_scheduler/schedule_upload_form.html', context=dict(form=form))

            messages.success(request, 'Schedule added!')
            return render(request, 'dock_scheduler/schedule_upload_form.html', context)

        else:
            messages.warning(request, 'Check the form for errors')
            context['form'] = form
            return render(request, 'dock_scheduler/schedule_upload_form.html', context)
    else:
        return render(request, 'dock_scheduler/schedule_upload_form.html', context)


@staff_member_required(login_url=reverse_lazy('login'))
def order_upload(request):
    if request.method == 'POST':
        form = UploadOrders(request.POST, request.FILES)
        if form.is_valid():
            try:
                handle_orders(request.FILES['file'])
            except (ValueError, TypeError, IndexError):
                messages.warning(request, 'Something went wrong while handling your file. '
                                          'Make sure you have the right file and that no typos are present in it.')
                return render(request, 'dock_scheduler/order_upload_form.html', context=dict(form=form))

            messages.success(request, 'Orders added successfully!')
            return redirect('/')

        else:
            messages.warning(request, 'Invalid file.')
            return render(request, 'dock_scheduler/order_upload_form.html', context=dict(form=form))
    else:
        form = UploadOrders()
        return render(request, 'dock_scheduler/order_upload_form.html', context=dict(form=form))


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


class ActivityView(View):

    def get(self, request, *args, **kwargs):
        view = ActivityDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            order = form.cleaned_data.get('order')
            driver = form.cleaned_data.get('driver')
            activity = form.cleaned_data.get('activity')
            dock_number = form.cleaned_data.get('dock_number')
            day = form.cleaned_data.get('day')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')

            # making sure the requested activity is the same as the one in the order
            order_query = Order.objects.filter(number=order, activity=activity)
            if len(order_query) == 0:
                messages.warning(request, "Order's activity doesn't match the one you want to book.")
                return redirect('activity-detail', pk=self.kwargs['pk'])

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


class BookingView(View):
    context = {
        'form': BookingManagement(),
        'title': 'My bookings',
    }

    def get(self, request, *args, **kwargs):
        return render(request, 'dock_scheduler/myreservations.html', self.context)

    def post(self, request, *args, **kwargs):
        form = BookingManagement(request.POST)
        if form.is_valid():
            driver = form.cleaned_data.get('driver')
            order = form.cleaned_data.get('order')
            reservation = Booking.objects.filter(driver=driver, order__pk=order)

            self.context = {
                'form': form,
                'bookings': reservation,
                'title': 'Results',
            }

            if len(reservation) == 0:
                messages.warning(request, 'No matching bookings')
                # return render(request, 'dock_scheduler/myreservations.html', self.context)
                return render(request, 'dock_scheduler/myreservations.html', self.context)

            else:
                return render(request, 'dock_scheduler/myreservations.html', self.context)
        else:
            # if the form is not valid
            self.context['form'] = form
            self.context['title'] = 'Error'
            return render(request, 'dock_scheduler/myreservations.html', self.context)


class BookingDetailView(DetailView):
    model = Booking


class BookingDelete(DeleteView):
    model = Booking
    success_url = '/'


def tft_screen(request):
    bookings = Booking.objects.filter(dock_activity__time_segment__day=today)
    return render(request, 'dock_scheduler/tft_screen.html', context=dict(bookings=bookings))
