from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("appointments/api/datatable/", views.AppointmentDataTableAjaxView.as_view(), name="datatable"),
    path("appointments/", views.AppointmentListView.as_view(), name="list"),
    path("appointments/add/", views.AppointmentCreateView.as_view(), name="create"),
    path("appointments/<int:pk>/edit/", views.AppointmentUpdateView.as_view(), name="update"),
    path("appointments/<int:pk>/delete/", views.AppointmentDeleteView.as_view(), name="delete"),
]
