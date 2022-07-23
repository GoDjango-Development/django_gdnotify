PLUGIN_NAME = "GDNOTIFY"
INSTALLED_APPS = [
    ...,
    "gdnotify"
]

INSTALLED_PLUGINS = {
    "GDNOTIFY": {
        "version": "1.0.0",
        "dependant": "dotted.path.to.Model",
        "admin_parents": {
        },
        "dependant_identifier": "username",
        "admin_sites": [

        ],
        "super_admin_sites": [   
        ]
    }
}
#ROOT_URLCONF = 'intercloud.urls'