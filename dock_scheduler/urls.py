from django.urls import path
from . import views
from .views import ActivityView, BookingView, BookingDetailView, BookingDelete

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('activity/<int:pk>/', ActivityView.as_view(), name='activity-detail'),
    path('lookup/', BookingView.as_view(), name='scheduler-mybookings'),
    path('lookup/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('lookup/<int:pk>/delete/', BookingDelete.as_view(), name='booking-delete'),
    path('schedule/', views.scheduleupload, name='scheduler-schedule'),

]
