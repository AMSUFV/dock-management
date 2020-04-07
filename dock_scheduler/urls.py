from django.urls import path
from . import views
from .views import DetailView

urlpatterns = [
    path('', views.home, name='scheduler-home'),
    path('activity/<int:pk>/', DetailView.as_view(), name='activity-detail'),
    path('lookup/', views.mybookings, name='scheduler-mybookings'),
    path('schedule/', views.scheduleupload, name='scheduler-schedule'),

]
