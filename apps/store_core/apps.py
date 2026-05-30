from django.apps import AppConfig


class StoreCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.store_core'
    verbose_name = 'База магазина (таблицы Prisma)'
