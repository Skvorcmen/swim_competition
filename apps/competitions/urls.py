from django.urls import path
from apps.competitions.views import (
    DownloadTemplateView,
    UploadApplicationView,
    FormHeatsView,
    ViewHeatsView,
    EnterResultsView,
    EventResultsView,
)

urlpatterns = [
    path(
        '<int:competition_id>/download-template/',
        DownloadTemplateView.as_view(),
        name='download_template'
    ),
    path(
        '<int:competition_id>/upload-application/',
        UploadApplicationView.as_view(),
        name='upload_application'
    ),
    path(
        '<int:competition_id>/form-heats/',
        FormHeatsView.as_view(),
        name='form_heats'
    ),
    path(
        '<int:competition_id>/heats/',
        ViewHeatsView.as_view(),
        name='view_heats'
    ),
    path(
        'heat/<int:heat_id>/enter-results/',
        EnterResultsView.as_view(),
        name='enter_results'
    ),
    path(
        'event/<int:event_id>/results/',
        EventResultsView.as_view(),
        name='event_results'
    ),
]

