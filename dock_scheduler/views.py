from django.shortcuts import render

docks = [
    {
        'id': '0',
        'driver': '4213KFN',
        'order': '144326',
        'type': 'Large',
        'status': 'Booked'
    },
    {
        'id': '1',
        'driver': '5619HYI',
        'order': '997351',
        'type': 'Large',
        'status': 'Free'
    },
]


def home(request):
    context = {
        'docks': docks
    }
    return render(request, 'dock_scheduler/home.html', context)


def book(request):
    return render(request, 'dock_scheduler/book.html', dict(title='Booking'))
