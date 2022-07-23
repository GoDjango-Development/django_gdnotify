# GoDjango Notify
This package allows you to set in your django site a notification system that works along with 
tfprotocol sending a notification for each user who has GoDjango Notify APK in his phone installed
## How to use
```py settings.py
PLUGIN_NAME = "GDNOTIFY"
INSTALLED_APPS = [
    ...,
    "gdnotify"
]

INSTALLED_PLUGINS = {
    "GDNOTIFY": {
        "version": "1.0.0", # For version control purposes
        "dependant": "dotted.path.to.Model", # For dependant model, which it means that for example, if you have a model that needs to be identified for others models or controllers you can set this to something different than None, for example auth.User which will allows you to have a foreign key in this model pointing to auth.Model
        "admin_parents": {
            # Each admin parent set here must have its key as admin classes in admin.py [SuperGoDjangoNotifyAdmin, GoDjangoNotifyAdmin]
        },
        "dependant_identifier": "username",
        "admin_sites": [
            # Admin sites where to register all gdnotify admin views, default: default site
        ],
        "super_admin_sites": [   
            # Admin sites where to register all gdnotify admin privileged views, default: default site, must have admin_sites setted or this will not work... if you only have privileged users then you may want to use admin_sites instead.
        ]
    }
}

```