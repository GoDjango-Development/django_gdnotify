from django.test import TestCase
from .models import GoDjangoNotify, GoDjangoNotifyFolders
from django.contrib.auth.models import User
#from django.contrib.auth.models import User
#from security.models import User

# Create your tests here.
class GDNTest(TestCase):
    def setUp(self, *args, **kwargs):
        gdnotify = GoDjangoNotify.objects.create(
            dependant=User.objects.create(
                username="test",
                password="test"
            )
        )
        GoDjangoNotifyFolders.objects.create(gdn=gdnotify, folder="one_folder", is_enabled=True)
    
    def test_gdn_push(self, *args, **kwargs):
        user = User.objects.filter(username="test").first()
        gdnotify = GoDjangoNotify.objects.filter(dependant=user).first()
        gdnotify.push(data={
            "tel": "+46764039298",
            "addr": "Mi direccion",
            "msg": "Una cosa",
            "date": "now"
        }, name=user.username)

    def test_gdn_tfm_push(self, *args, **kwargs):
        user = User.objects.filter(username="test").first()
        gdnotify = GoDjangoNotify.objects.filter(dependant=user).first()
        gdnotify.push(data={
            "tel": "+46764039298",
            "addr": "Mi direccion",
            "msg": "Una cosa",
            "date": "now",
            "tfm": "something",
        }, name=user.username)

    def test_gdn_clear(self, *args, **kwargs):
        user = User.objects.filter(username="test").first()
        gdnotify = GoDjangoNotify.objects.filter(dependant=user).first()
        gdnotify.godjangonotifyfolders_set.first().clear()
