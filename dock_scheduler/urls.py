from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('book/', views.book, name='scheduler-booking'),
    path('bookings/', views.bookings, name='scheduler-bookings')
]
