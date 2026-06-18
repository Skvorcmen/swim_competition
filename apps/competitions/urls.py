from django.urls import path
from apps.competitions.views import DownloadTemplateView, UploadApplicationView

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
]