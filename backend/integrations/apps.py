from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"

    def ready(self) -> None:
        # Import signal handlers so they are registered when Django starts.
        # The import must live here to avoid circular imports with core models.
        import integrations.signals  # noqa: F401
