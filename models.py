import json
import os
import re
from hashlib import sha256
from django_plugins import get_plugin
from glob import glob
from .settings import PLUGIN_NAME
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _, gettext as _n

gdn_structure = {
    "name": None,
    "tel": None,
    "addr": None,
    "msg":None,
    "date":None
}

def set_new_structure(new_struct):
    gdn_structure = new_struct

def path_exists(value:str):
    if os.path.exists(value):
        raise ValidationError(_("Given path already exists, please choose a new one"))

def is_secure_folder(value: str):
    temp = value[::-1].split(".", 1)
    if not temp[0] == "ds" or len(temp[1])/2 != 256/8:
        return False
    return True

def is_domain_name(value: str):
    if re.match(r"^[a-zA-Z0-9\.\-\_]+$", value) is None:
        raise ValidationError(_("Invalid domain name, please use one like tfproto.expresscuba.com"))
    
def is_subfolder(value:str, no_raise=False):
    if (os.path.exists(value) and os.path.isdir(value) or not os.path.exists(value)) and (
            not value.startswith(str(settings.BASE_DIR)
            )
        ):
        if not no_raise:
            raise ValidationError(_("Given path is not a subpath of our project folder :) you can't explore our filesystem"))
        else:
            return False
    return True

def enclose_func(func, *args):
    def wrapped(*paths, **kwargs):
        has_out_of_folder = (False in map(lambda path: is_subfolder(path), paths))
        if not has_out_of_folder:
            return func(*paths, **kwargs)
        return False
    return wrapped

@enclose_func
def rm(path: str, recursive=False):
    command = "rm %s '%s'"%("-r" if recursive else "", path)
    res = os.system(command) != 0
    return res

@enclose_func
def cp(path: str, new_path: str, recursive=False):
    command = "cp %s '%s' '%s'"%("-r" if recursive else "",path, new_path)
    res = os.system(command) != 0
    return res

@enclose_func
def mkdir(path: str, recursive: bool = False):
    command = "mkdir '%s' %s"%(path, "-p" if recursive else "")
    res = os.system(command) != 0
    return res
    
@enclose_func
def mv(path: str, new_path: str):
    command = "mv '%s' '%s'"%(path, new_path)
    res = os.system(command) != 0
    return res

plugin_dependant = get_plugin(PLUGIN_NAME).get("dependant")

class GoDjangoNotify(models.Model):
    base_path = models.CharField(_("Path to base folder"), 
        default=str(os.path.join(settings.BASE_DIR, "gdnjson")), max_length=250,
        validators=[is_subfolder])
    port = models.IntegerField(_("Tfprotocol Port"), default=10450)
    domain_name = models.CharField(_("Tfprotocol domain name"), default="tfproto.expresscuba.com", 
        validators=[is_domain_name, ],
        max_length=50
    )
    def push(self, data: dict=None, name:str="unknown", **kwargs):
        folders = GoDjangoNotifyFolders.objects.filter(gdn=self.id)
        for folder in folders:
            folder.push(data=data, name=name, **kwargs)

    def save(self, *args, **kwargs):
        if self.base_path == settings.BASE_DIR:
            print("DANGER ZONE CANNOT OVERWRITE PROJECT, ACTING NOW AGAINST A POSSIBLE DoS ATTACK... GUARDS UP")
            return
        
        if (not os.path.exists(self.base_path)):
            mkdir(self.base_path, recursive=True)
            folders = GoDjangoNotifyFolders.objects.filter(gdn=self.id)
            for folder in folders:
                mkdir(os.path.join(self.base_path, folder.folder))
        previous = GoDjangoNotify.objects.filter(id=self.id).first()
        if previous is not None and previous.base_path != self.base_path:
            mv(os.path.join(previous.base_path, "*"), self.base_path)
        
        return super().save(*args, **kwargs)

    def __str__(self):
        return _n("GoDjango Notify")

    class Meta:
        verbose_name = _("GoDjango Notify")
        verbose_name_plural = _("GDN Settings")


if plugin_dependant is not None and len(plugin_dependant) > 0:
    GoDjangoNotify.add_to_class("dependant", models.ForeignKey(plugin_dependant, on_delete=models.CASCADE))

# Create your models here.
class GoDjangoNotifyFolders(models.Model):
    gdn = models.ForeignKey(to="gdnotify.GoDjangoNotify", on_delete=models.CASCADE, default="")
    folder = models.CharField(_("Secure Folder"), default=_n("Save to generate the secure directory..."), max_length=256, )
    is_enabled = models.BooleanField(_("Is this folder enabled?"), default=False, 
    help_text=_("Mark this to successfully add or enable this folder..."))
    SECURE_FILE_NAME = ".secure"

    def check_args(self, **kwargs):
        for key in gdn_structure.keys():
            assert kwargs.get(key, False), "Missing key '%s' for this GDN Version"%key

    def push(self, data: dict=None, name:str="unknown", **kwargs):
        if data is None:
            data = kwargs
        path = os.path.join(self.gdn.base_path, self.folder)
        data["name"] = name
        self.check_args(**data)
        if not os.path.exists(path):
            mkdir(path, recursive = True)
        counter: int = len(os.listdir(path))
        name = "_".join((str(counter), name, str(int(now().timestamp())))) + ".json.tmp"
        temp_path = os.path.join(path, name)
        with open(temp_path, "x") as file:
            file.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=True))
            base_path, file_name = os.path.split(temp_path)
            file_name = ".".join(file_name.split(".")[:-1])
            os.rename(temp_path,  os.path.join(base_path, file_name))
    
    def clear(self, ):
        path = os.path.join(self.gdn.base_path, self.folder)
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
        with open(os.path.join(path, self.SECURE_FILE_NAME), "x"):
            pass
            
    def save(self, *args, **kwargs) -> None:
        if not is_secure_folder(self.folder):
            identifier = ""
            if hasattr(self.gdn, "dependant"):
                identifier = getattr(self.gdn.dependant, get_plugin(PLUGIN_NAME).get("dependant_identifier", None), "username")
            self.folder = sha256((str(now()) + str(identifier)).encode()).hexdigest() + ".sd"
        path = os.path.join(self.gdn.base_path, self.folder)
        if is_secure_folder(self.folder):
            if not os.path.exists(path):
                mkdir(path)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return _n("GoDjango Notify Folder: %s")%self.folder
    
    class Meta:
        verbose_name = _("GDN Folders")
        verbose_name_plural = _("GDN Folders")