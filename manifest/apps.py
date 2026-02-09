from django.apps import AppConfig


class ManifestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manifest'

    def ready(self):
        import manifest.signals
