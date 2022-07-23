from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GdnotifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gdnotify'
    verbose_name: str = _("Installed Apps")
    def ready(self, *args, **kwargs):
        pass