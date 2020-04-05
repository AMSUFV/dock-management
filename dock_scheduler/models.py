from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Dock(models.Model):
    # dock type
    TRAILER = 'TR'
    VAN = 'VA'
    TARPAULIN = 'CA'
    DOCK_TYPE_CHOICES = [
        (TRAILER, 'Trailer'),
        (VAN, 'Van'),
        (TARPAULIN, 'Tarpaulin truck'),
    ]

    # dock state
    FREE = 'FR'
    OCCUPIED = 'OC'
    DOCK_STATE_CHOICES = [
        (FREE, 'Free'),
        (OCCUPIED, 'Occupied'),
    ]

    number = models.PositiveIntegerField(
        primary_key=True,
    )
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

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'Dock {self.number}'


class TimeSegment(models.Model):
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # TODO: add validator so segments from the same day can't overlap

    def __str__(self):
        return f'{self.day}, {self.start_time} - {self.end_time}'


class DockActivity(models.Model):
    # foreign key
    dock = models.ForeignKey(
        Dock,
        on_delete=models.CASCADE,
    )

    time_segment = models.ForeignKey(
        TimeSegment,
        on_delete=models.CASCADE
    )

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
        return f'{self.dock} | {self.time_segment} | {self.activity}'

    class Meta:
        verbose_name_plural = 'Dock activities'
        constraints = [
            models.UniqueConstraint(fields=['dock', 'time_segment'], name='unique_activity')
        ]


class Order(models.Model):
    number = models.CharField(
        primary_key=True,
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')],
    )

    def __str__(self):
        return f'ORDER: {self.number}'


class Booking(models.Model):
    # foreign keys
    time_segment = models.ForeignKey(
        TimeSegment,
        on_delete=models.CASCADE,
        unique=True,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        unique=True,
    )

    # driver's license plate
    driver = models.CharField(
        max_length=15
    )

    def __str__(self):
        return f'{self.driver} at {str(self.time_segment)}'



