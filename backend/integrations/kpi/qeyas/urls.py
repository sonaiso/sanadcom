from django.urls import path

from .views import QeyasExecutiveSummaryView, QeyasWebhookView

app_name = "qeyas"

urlpatterns = [
    path(
        "executive-summary/",
        QeyasExecutiveSummaryView.as_view(),
        name="executive-summary",
    ),
    path(
        "webhook/",
        QeyasWebhookView.as_view(),
        name="webhook",
    ),
]
