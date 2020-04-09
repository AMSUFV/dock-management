from django.urls import path
from . import views
from .views import ActivityView, BookingView, BookingDetailView, BookingDelete, Home
urlpatterns = [
    path('', Home.as_view(), name='scheduler-home'),
    path('search/<vehicle>/<activity>/<day>/<start_time>/<end_time>/', Home.as_view(), name='scheduler-search'),
    path('activity/<int:pk>/', ActivityView.as_view(), name='activity-detail'),
    path('lookup/', BookingView.as_view(), name='scheduler-mybookings'),
    path('lookup/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('lookup/<int:pk>/delete/', BookingDelete.as_view(), name='booking-delete'),
    path('schedule/', views.scheduleupload, name='scheduler-schedule'),
    path('upload_orders/', views.order_upload, name='scheduler-upload-orders'),
    path('tft/', views.tft_screen, name='scheduler-tft'),

]

