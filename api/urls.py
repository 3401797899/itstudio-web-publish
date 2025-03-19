from django.urls import path
from .views import ConfigurationView, DomainConfigListCreateView, DomainConfigRetrieveUpdateDestroyView

urlpatterns = [
    path('config/', ConfigurationView.as_view(), name='configuration'),
    path('domains/', DomainConfigListCreateView.as_view(), name='domain-list-create'),
    path('domains/<int:pk>/', DomainConfigRetrieveUpdateDestroyView.as_view(), name='domain-detail'),
]