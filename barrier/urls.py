from django.urls import path
from . import views

urlpatterns = [
    path('', views.BarrierControl.as_view(), name='barrier-control')
]