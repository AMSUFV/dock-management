from django.db import models
from django.contrib.auth.models import User


class Dock(models.Model):
    # dock type
    TRAILER = 'TR'
    FURGONETA = 'FU'
    LONA = 'LO'
    DOCK_TYPE_CHOICES = [
        (TRAILER, 'Trailer'),
        (FURGONETA, 'Furgoneta'),
        (LONA, 'Lona'),
    ]

    # dock state
    FREE = 'FR'
    OCCUPIED = 'OC'
    DOCK_STATE_CHOICES = [
        (FREE, 'Free'),
        (OCCUPIED, 'Occupied'),
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
