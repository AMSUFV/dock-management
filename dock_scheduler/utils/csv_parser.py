import datetime
from dock_scheduler.models import Dock, TimeSegment, DockActivity


def handle_schedule(f, day, name='schedule.csv'):

    route = f'dock_scheduler/static/dock_scheduler/{name}'
    preprocess(f, route)

    docks, segments, activities = parse(route)
    cu_docks(docks)
    cu_segments(segments, day)
    cu_activities(activities, day)


def handle_orders(f, name='orders.csv'):
    route = f'dock_scheduler/static/dock_scheduler/{name}'
    preprocess(f, route)


def preprocess(file, route):
    with open(route, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def cu_docks(docks):

    for dock in docks:
        number = dock['number']
        category = translate_category(dock['category'])

        existing_dock = Dock.objects.filter(number=number)
        if len(existing_dock):
            existing_dock.delete()

        new_dock = Dock(number=number, category=category)
        new_dock.save()


def cu_segments(segments, day):

    existing_segments = TimeSegment.objects.filter(day=day)
    if len(existing_segments):
        existing_segments.delete()

    for segment in segments:
        start_time = segment['start_time']
        end_time = segment['end_time']

        new_segment = TimeSegment(day=day, start_time=start_time, end_time=end_time)
        new_segment.save()


def cu_activities(activities, day):

    for activity in activities:
        dock_number = activity['dock_number']
        start_time = activity['time_segment']['start_time']
        end_time = activity['time_segment']['end_time']
        activity = translate_activity(activity['activity'])

        dock = Dock.objects.filter(number=dock_number).first()
        time_segment = TimeSegment.objects.filter(day=day, start_time=start_time, end_time=end_time).first()

        new_activity = DockActivity(dock=dock, time_segment=time_segment, activity=activity)
        new_activity.save()


def translate_activity(activity):

    if activity.lower() in ['load', 'carga']:
        translation = 'LO'
    elif activity.lower() in ['unload', 'descarga']:
        translation = 'UL'
    else:
        translation = 'UA'
    return translation


def translate_category(category):

    if category.lower() in ['lona', 'tarpaulin truck']:
        translation = 'TT'
    elif category.lower() in ['furgoneta', 'van']:
        translation = 'VA'
    else:
        translation = 'TR'
    return translation


def parse(file_name):

    docks = []
    segments = []
    activities = []
    delimiter = ';'

    with open(file_name, 'r') as file:
        for i, line in enumerate(file):
            columns = line.rstrip().split(delimiter)
            if i == 0:
                for segment in columns[2:]:
                    start_time, end_time = segment.split('-')

                    # conversion to datetime
                    hour, minutes = start_time.split(':')
                    start_time = datetime.time(int(hour), int(minutes))
                    hour, minutes = end_time.split(':')
                    end_time = datetime.time(int(hour), int(minutes))

                    segments.append(dict(start_time=start_time, end_time=end_time))
            else:
                dock_number = columns[0]  # number column
                dock_category = columns[1]  # vehicle column
                docks.append(dict(number=dock_number, category=dock_category))

                day_activities = columns[2:]
                for activity, segment in zip(day_activities, segments):
                    activities.append(dict(dock_number=dock_number, time_segment=segment, activity=activity))

    return docks, segments, activities


def parse_orders(file_name):
    pass
