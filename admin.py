from django.contrib import admin
from django.utils.timezone import now
from hashlib import sha256
from .models import *
from django.conf import settings
from .settings import PLUGIN_NAME
from solo.admin import SingletonModelAdmin
from django_plugins import get_plugin, import_string

class GoDjangoNotifyFolderInline(
        import_string(get_plugin(PLUGIN_NAME).get("admin_parents", {}).get("GoDjangoNotifyFolderInline", "django.contrib.admin.TabularInline"))
    ):
    model = GoDjangoNotifyFolders
    #exclude = ("folder", )
    readonly_fields = ("folder",)

    def autogenerated_folder(self, model, *args, **kwargs):
        return sha256(str(now()).encode()).hexdigest()

#@admin.register(GoDjangoNotify, site=client)
class GoDjangoNotifyAdmin(
        import_string(get_plugin(PLUGIN_NAME).get("admin_parents", {}
        ).get("GoDjangoNotifyAdmin", "solo.admin.SingletonModelAdmin"))):
    list_display = ("domain_name", "port",)
    list_display_links = ("domain_name", "port",)
    exclude = ("base_path", "user")
    readonly_fields= ("port", "domain_name",)
    inlines = (GoDjangoNotifyFolderInline, )

#@admin.register(GoDjangoNotify, site=staff)
class SuperGoDjangoNotifyAdmin(
    import_string(get_plugin(PLUGIN_NAME).get("admin_parents", {}
        ).get("SuperGoDjangoNotifyAdmin", "solo.admin.SingletonModelAdmin"))):
    list_display = ("base_path_preview","domain_name", "port",)
    list_editable = ("domain_name", "port",)
    exclude = ("user", )
    inlines = (GoDjangoNotifyFolderInline, )
    def base_path_preview(self, model, *args, **kwargs):
        max_length = 30
        if len(model.base_path) > max_length:
            path = str(model.base_path)[::-1][:max_length][::-1]
            path = path.split(os.path.sep, 1)[1]
            return ".../" + path
        return model.base_path

admin_sites = get_plugin(PLUGIN_NAME).get("admin_sites", [])    
super_admin_sites = get_plugin(PLUGIN_NAME).get("super_admin_sites", [])

if len(admin_sites) == 0 and len(super_admin_sites) == 0:
    admin.site.register(GoDjangoNotify, admin_class=GoDjangoNotifyAdmin)

if len(super_admin_sites) > 0: 
    for admin_site in admin_sites:
        site: admin.AdminSite = import_string(admin_site)
        site.register(GoDjangoNotify, admin_class=GoDjangoNotifyAdmin)
elif len(admin_sites) > 0:
    for admin_site in admin_sites:
        site: admin.AdminSite = import_string(admin_site)
        site.register(GoDjangoNotify, admin_class=SuperGoDjangoNotifyAdmin)

if len(admin_sites) > 0:
    for admin_site in super_admin_sites:
        site: admin.AdminSite = import_string(admin_site)
        site.register(GoDjangoNotify, admin_class=SuperGoDjangoNotifyAdmin)
