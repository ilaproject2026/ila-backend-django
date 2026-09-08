from django.apps import AppConfig


class GlobalRealEstateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Applications.GlobalRealEstate'
    label = 'GlobalStudio'  # Keep original label so existing DB tables & migrations are preserved
    verbose_name = 'ILA Global Real Estate & Co-Living Platform'
