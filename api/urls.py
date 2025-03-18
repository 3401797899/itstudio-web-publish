from django.urls import path
from .views import ConfigurationView

urlpatterns = [
    path('config/', ConfigurationView.as_view(), name='configuration'),
]