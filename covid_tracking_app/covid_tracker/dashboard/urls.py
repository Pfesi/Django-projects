from django.urls import path

from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name="dashboard_home"),
    path('selectCountry', views.selectCountry, name="selectCountry")
]
