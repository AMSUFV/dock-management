from django import forms
from django.core.validators import RegexValidator


class BookingForm(forms.Form):
    # Dock number
    dock_number = forms.IntegerField(
        label='Número de muelle',
        min_value=0)

    # Booking day and time
    day = forms.DateField(
        label='Fecha',
        help_text='Con formato año-mes-día. Ej: (2020-03-25)'
    )
    start_time = forms.TimeField(label='Hora de inicio')
    end_time = forms.TimeField(label='Hora de fin')

    # Activity to perform
    LOAD = 'CA'
    UNLOAD = 'DE'
    ACTIVITIES = [
        (LOAD, 'Carga'),
        (UNLOAD, 'Descarga'),
    ]
    activity = forms.CharField(
        label='Actividad a realizar',
        widget=forms.Select(choices=ACTIVITIES)
    )

    # Order ID
    order = forms.CharField(
        label='Número de pedido',
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')]
    )

    # Driver's license plate
    driver = forms.CharField(
        label='Matrícula',
        max_length=15,
    )


# Form used to consult and delete the reservation
class BookingManagement(forms.Form):
    # Driver's license plate
    driver = forms.CharField(
        label='Matrícula',
        max_length=15,
    )

    # Order ID
    order = forms.CharField(
        label='Número de pedido',
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')],
    )
