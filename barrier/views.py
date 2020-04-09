import datetime

from django.contrib import messages
from django.shortcuts import render
from django.views import View

from dock_scheduler.models import Booking
from .forms import BarrierControlForm


class BarrierControl(View):

    def get(self, request, *args, **kwargs):
        form = BarrierControlForm()
        return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))

    def post(self, request, *args, **kwargs):
        form = BarrierControlForm(request.POST)
        if form.is_valid():
            driver = form.cleaned_data.get('driver')
            day = form.cleaned_data.get('day')
            hour = form.cleaned_data.get('hour')
            direction = form.cleaned_data.get('direction')

            if direction == 'IN':
                # if form is valid, find booking and its starting time
                bookings = Booking.objects.filter(dock_activity__time_segment__day=day, driver=driver)

                # if there are no bookings for this driver, we return an error message
                if len(bookings) == 0:
                    messages.info(request, 'No bookings for that driver today')
                    return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))

                # if there are, assuming there's only one, we find out if the driver is either too early or too late
                else:
                    booking = bookings.first()
                    start_time = booking.dock_activity.time_segment.start_time
                    # The driver can be either 10 minutes early or late
                    minutes = 10
                    lower_bound = (datetime.datetime.combine(datetime.date(1, 1, 1), start_time)
                                   - datetime.timedelta(minutes=minutes)).time()
                    upper_bound = (datetime.datetime.combine(datetime.date(1, 1, 1), start_time)
                                   + datetime.timedelta(minutes=minutes)).time()

                    # if the driver is between time limits
                    if upper_bound >= hour >= lower_bound:
                        # we check is the dock is currently free
                        dock = booking.dock_activity.dock
                        # if it is, we'll open the barrier
                        if dock.state == 'FR':
                            messages.success(request, 'Barrier open. Have a nice day')
                            dock.state = 'OC'
                            dock.save()
                            return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))
                        else:
                            messages.info(request, "The dock is occupied. Please wait until it's free.")

                    elif hour > upper_bound:
                        messages.warning(request, f"You are too late. Booking was scheduled for {start_time}.")

                    else:
                        messages.info(request, f"You are too early. Please wait until {start_time}.")

                    return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))
            else:
                bookings = Booking.objects.filter(dock_activity__time_segment__day=day, driver=driver)
                if len(bookings) == 0:
                    messages.warning(request, "You shouldn't be here today. You have no reservations.")
                    return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))
                else:
                    booking = bookings.first()
                    dock = booking.dock_activity.dock
                    dock.state = 'FR'
                    dock.save()
                    booking.delete()
                    messages.success(request, 'Barrier open. Have a nice day.')
                    return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))
        else:
            return render(request, 'barrier/barrier_simulation.html', context=dict(form=form))