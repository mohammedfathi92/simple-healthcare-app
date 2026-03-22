from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("patients/api/datatable/", views.PatientDataTableAjaxView.as_view(), name="datatable"),
    path(
        "patients/api/schedule-search/",
        views.PatientScheduleSearchFragmentView.as_view(),
        name="schedule_search",
    ),
    path("patients/", views.PatientListView.as_view(), name="list"),
    path("patients/add/", views.PatientCreateView.as_view(), name="create"),
    path("patients/<int:pk>/", views.PatientDetailView.as_view(), name="detail"),
    path("patients/<int:pk>/edit/", views.PatientUpdateView.as_view(), name="update"),
    path("patients/<int:pk>/delete/", views.PatientDeleteView.as_view(), name="delete"),
]
