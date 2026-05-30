from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    verbose_name = 'Common utilities'

    def ready(self):
        # Register drf-spectacular auth schemes for custom auth classes.
        from apps.common import openapi_auth  # noqa: F401
