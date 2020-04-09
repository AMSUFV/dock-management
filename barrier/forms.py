import datetime

from django import forms
from django.core.validators import RegexValidator


class BarrierControlForm(forms.Form):
    today = datetime.date.today()
    # Driver's license plate
    driver = forms.CharField(
        label='License plate',
        max_length=15,
        validators=[RegexValidator(r'^\w{1,15}$', 'License plate can only contain numbers and letters.')]
    )

    day = forms.DateField(
        label='Date',
        help_text=f'Year-Month-Day. Today: {today}',
    )
    hour = forms.TimeField(
        label='Current time',
        help_text='Hour:Minute format: 14:30',
    )

    ENTRY = 'IN'
    EXIT = 'OUT'
    CHOICES = [
        (ENTRY, 'Going in'),
        (EXIT, 'Going out')
    ]
    direction = forms.CharField(
        label='Where are you going?',
        widget=forms.Select(choices=CHOICES),
    )

    def clean_day(self):
        day = self.cleaned_data['day']

        if day is not None:
            if day < datetime.date.today():
                raise forms.ValidationError("You can't go back to the past McFly!")

        return day

    def clean_driver(self):
        driver = self.cleaned_data['driver']
        driver = driver.upper()
        return driver
