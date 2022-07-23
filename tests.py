from django.test import TestCase
from .models import GoDjangoNotify, GoDjangoNotifyFolders
from django.contrib.auth.models import User
#from django.contrib.auth.models import User
#from security.models import User

# Create your tests here.
class GDNTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.gdnotify = GoDjangoNotify.objects.create(
            dependant=User.objects.create(
                username="test",
                password="test"
            )
        )
        self.folders = GoDjangoNotifyFolders.objects.create(gdn=self.gdnotify, folder="one_folder", is_enabled=True)
    
    def test_gdn_push(self, *args, **kwargs):
        self.gdnotify.push(data={
            "tel": "+46764039298",
            "addr": "Mi direccion",
            "msg": "Una cosa",
            "date": "now"
        }, name=self.gdnotify.dependant.username)
        self.gdnotify.push(data={
            "tel": "+46764039298",
            "addr": "Mi direccion",
            "msg": "Otra cosa",
            "date": "now"
        }, name=self.gdnotify.dependant.username)

    def test_gdn_tfm_push(self, *args, **kwargs):
        self.gdnotify.push(data={
            "tel": "+46764039298",
            "addr": "Mi direccion",
            "msg": "Una cosa",
            "date": "now",
            "tfm": "something",
        }, name=self.gdnotify.dependant.username)

    def test_gdn_clear(self, *args, **kwargs):
        self.gdnotify.godjangonotifyfolders_set.first().clear()
