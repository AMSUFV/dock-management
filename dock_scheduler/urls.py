from django.urls import path
from django.views.decorators.http import require_POST
from . import views
from .views import ActivityDetailView, BookingFormView, DetailView

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('activity/<int:pk>/', DetailView.as_view(), name='activity-detail'),
    path('book/', views.book, name='scheduler-booking'),
    path('lookup/', views.mybookings, name='scheduler-mybookings'),
    path('schedule/', views.scheduleupload, name='scheduler-schedule'),

]
