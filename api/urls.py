from django.urls import path
from .views import (
    ConfigurationView, 
    DomainConfigListCreateView, 
    DomainConfigRetrieveUpdateDestroyView, 
    DomainConfigPreviewView, 
    DomainConfigWriteView, 
    DomainConfigRestartView,
    LoginView,
    LogoutView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('config/', ConfigurationView.as_view(), name='configuration'),
    path('domains/', DomainConfigListCreateView.as_view(), name='domain-list-create'),
    path('domains/<int:pk>/', DomainConfigRetrieveUpdateDestroyView.as_view(), name='domain-detail'),
    path('domains/preview/', DomainConfigPreviewView.as_view(), name='domain-preview'),
    path('domains/write/', DomainConfigWriteView.as_view(), name='domain-write'),
    path('domains/restart/', DomainConfigRestartView.as_view(), name='domain-restart'),
]