from django.urls import path
from django.views.decorators.http import require_POST
from . import views
from .views import ActivityDetailView, BookingFormView

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('activity/<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),
    path('booking_form/', require_POST(BookingFormView.as_view()), name='activity-form'),
    path('book/', views.book, name='scheduler-booking'),
    path('lookup/', views.mybookings, name='scheduler-mybookings'),
    path('schedule/', views.scheduleupload, name='scheduler-schedule'),

]
