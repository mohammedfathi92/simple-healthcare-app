from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.ProviderLoginView.as_view(), name="login"),
    path("logout/", views.ProviderLogoutView.as_view(), name="logout"),
    path("dashboard/", views.ProviderDashboardView.as_view(), name="dashboard"),
]
