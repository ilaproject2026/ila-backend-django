from django.apps import AppConfig


class CorporateAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Applications.CorporateAdmin'
    label = 'CorporateAdmin'
    verbose_name = 'Corporate Admin'
