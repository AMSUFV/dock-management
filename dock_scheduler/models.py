from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Dock(models.Model):
    # dock type
    TRAILER = 'TR'
    FURGONETA = 'FU'
    LONA = 'LO'
    DOCK_TYPE_CHOICES = [
        (TRAILER, 'Trailer'),
        (FURGONETA, 'Furgoneta'),
        (LONA, 'Camión de lona'),
    ]

    # dock state
    FREE = 'FR'
    OCCUPIED = 'OC'
    DOCK_STATE_CHOICES = [
        (FREE, 'Libre'),
        (OCCUPIED, 'Ocupado'),
    ]

    number = models.SmallIntegerField()
    category = models.CharField(
        max_length=2,
        choices=DOCK_TYPE_CHOICES,
        default=TRAILER,
    )
    state = models.CharField(
        max_length=2,
        choices=DOCK_STATE_CHOICES,
        default=FREE,
    )

    def __str__(self):
        return f'Dock {self.number}'


class TimeSegment(models.Model):
    # foreign key
    dock = models.ForeignKey(Dock, on_delete=models.CASCADE)
    # segment
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # activity
    LOAD = 'CA'
    UNLOAD = 'DE'
    UNAVAILABLE = 'ND'
    ACTIVITIES = [
        (LOAD, 'Carga'),
        (UNLOAD, 'Descarga'),
        (UNAVAILABLE, 'No disponible'),
    ]
    activity = models.CharField(
        max_length=2,
        choices=ACTIVITIES)

    def __str__(self):
        return f'D{self.dock.number} | {self.activity} | {self.start_time} - {self.end_time}'


class Booking(models.Model):
    # foreign key
    time_segment = models.ForeignKey(TimeSegment, on_delete=models.CASCADE)
    # driver's license plate
    driver = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.driver} at {str(self.time_segment)}'


class Order(models.Model):
    number = models.CharField(
        primary_key=True,
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')],
    )

    def __str__(self):
        return f'ORDER NO: {self.number}'
