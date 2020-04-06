from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Dock(models.Model):
    # dock type
    TRAILER = 'TR'
    VAN = 'VA'
    TARPAULIN = 'CA'
    DOCK_CATEGORY_CHOICES = [
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
        choices=DOCK_CATEGORY_CHOICES,
        default=TRAILER,
    )
    state = models.CharField(
        max_length=2,
        choices=DOCK_STATE_CHOICES,
        default=FREE,
    )

    def __str__(self):
        return f'Dock {self.number}'

    def category_verbose(self):
        return dict(Dock.DOCK_CATEGORY_CHOICES)[self.category]

    def state_verbose(self):
        return dict(Dock.DOCK_STATE_CHOICES)[self.state]

    class Meta:
        ordering = ['number']


class TimeSegment(models.Model):
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.day}, {self.start_time} - {self.end_time}'

    # TODO: add validator so segments from the same day can't overlap
    def clean(self):
        # making sure that the time slice makes sense
        if self.start_time > self.end_time:
            raise ValidationError('Start time should happen before end time.')
        # making sure the time slice doesn't invade a different slice
        query = TimeSegment.objects.filter(day=self.day)
        for ts in query:
            if ts.end_time > self.start_time > ts.start_time:
                raise ValidationError(f'Time slice start invades a different one. {ts.start_time} to {ts.end_time}')
            if ts.start_time < self.end_time < ts.end_time:
                raise ValidationError(f'Time slice end invades a different one. {ts.start_time} to {ts.end_time}')


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
        (LOAD, 'Load'),
        (UNLOAD, 'Unload'),
        (UNAVAILABLE, 'Unavailable'),
    ]
    activity = models.CharField(
        max_length=2,
        choices=ACTIVITIES)

    def __str__(self):
        return f'{self.dock} | {self.time_segment} | {self.activity_verbose()}'

    def activity_verbose(self):
        return dict(DockActivity.ACTIVITIES)[self.activity]

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
    dock_activity = models.ForeignKey(
        DockActivity,
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
        return f'{self.driver} at {str(self.dock_activity)}'
