from django import forms
from django.core.validators import RegexValidator
import datetime


# TODO: check that the day must be greater or equal than today
class BookingForm(forms.Form):
    # Activity to perform
    LOAD = 'CA'
    UNLOAD = 'DE'
    ACTIVITIES = [
        (LOAD, 'Load'),
        (UNLOAD, 'Unload'),
    ]

    # vehicle type
    TRAILER = 'TR'
    VAN = 'VA'
    TARPAULIN = 'CA'
    DOCK_TYPE_CHOICES = [
        (TRAILER, 'Trailer'),
        (VAN, 'Van'),
        (TARPAULIN, 'Tarpaulin truck'),
    ]

    # Order ID
    order = forms.CharField(
        label='Order number',
        min_length=6,
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')]
    )

    # Driver's license plate
    driver = forms.CharField(
        label='License plate',
        max_length=15,
    )

    # Vehicle tu use
    vehicle = forms.CharField(
        label='Vehicle',
        widget=forms.Select(choices=DOCK_TYPE_CHOICES)
    )

    # Activity to perform
    activity = forms.CharField(
        label='Activity',
        widget=forms.Select(choices=ACTIVITIES)
    )

    # Dock number
    dock_number = forms.IntegerField(
        label='Dock number',
        min_value=0)

    # Booking day and time
    day = forms.DateField(
        label='Date',
        help_text='Year-Month-Day format: 2020-03-25'
    )
    start_time = forms.TimeField(
        label='Start time',
        help_text='Hour:Minute format: 14:30',
    )
    end_time = forms.TimeField(
        label='End time',
        help_text='Hour:Minute format: 14:30',
    )


# Form used to consult and delete the reservation
class BookingManagement(forms.Form):
    # Order ID
    order = forms.CharField(
        label='Order number',
        min_length=6,
        max_length=6,
        validators=[RegexValidator(r'^\d{1,6}$', 'Order can only contain numbers.')],
    )

    # Driver's license plate
    driver = forms.CharField(
        label='License plate',
        max_length=15,
        validators=[RegexValidator(r'^\w{1,15}$', 'License plate can only contain numbers and letters.')]
    )

    def clean_driver(self):
        driver = self.cleaned_data['driver']
        driver = driver.upper()
        return driver


class SearchForm(forms.Form):
    # Activity to perform
    LOAD = 'LO'
    UNLOAD = 'UL'
    ACTIVITIES = [
        (LOAD, 'Load'),
        (UNLOAD, 'Unload'),
    ]

    # vehicle type
    TRAILER = 'TR'
    VAN = 'VA'
    TARPAULIN = 'TT'
    DOCK_TYPE_CHOICES = [
        (TRAILER, 'Trailer'),
        (VAN, 'Van'),
        (TARPAULIN, 'Tarpaulin truck'),
    ]

    # Vehicle
    vehicle = forms.CharField(
        label='Vehicle',
        widget=forms.Select(choices=DOCK_TYPE_CHOICES)
    )

    activity = forms.CharField(
        label='Activity',
        widget=forms.Select(choices=ACTIVITIES),
    )

    # Booking day and time
    day = forms.DateField(
        label='Date',
        help_text='Year-Month-Day format: 2020-03-25',
        required=False,
    )
    start_time = forms.TimeField(
        label='Start time',
        help_text='Hour:Minute format: 14:30',
        required=False,
    )
    end_time = forms.TimeField(
        label='End time',
        help_text='Hour:Minute format: 15:30',
        required=False,
    )

    def clean_day(self):
        reservation_day = self.cleaned_data['day']

        if reservation_day is not None:
            if reservation_day < datetime.date.today():
                raise forms.ValidationError("You can't go back to the past McFly!")

        return reservation_day

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time is not None and end_time is not None:
            if start_time > end_time:
                raise forms.ValidationError({'start_time': 'Start time happens after end time'})


class DailySchedule(forms.Form):
    # Booking day and time
    day = forms.DateField(
        label='Date',
        help_text='Year-Month-Day format: 2020-03-25'
    )
    schedule = forms.FileField()
