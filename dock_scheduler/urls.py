from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('book/', views.book, name='scheduler-booking'),
    path('lookup/', views.mybookings, name='scheduler-mybookings'),
]
