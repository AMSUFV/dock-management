from django import forms
from django.core.validators import RegexValidator


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
    # Driver's license plate
    driver = forms.CharField(
        label='License plate',
        max_length=15,
    )

    # Order ID
    order = forms.CharField(
        label='Order number',
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')],
    )


class SearchForm(forms.Form):
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


class DailySchedule(forms.Form):
    # Booking day and time
    day = forms.DateField(
        label='Date',
        help_text='Year-Month-Day format: 2020-03-25'
    )
    info = forms.FileField()
