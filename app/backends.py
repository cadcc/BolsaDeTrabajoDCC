from django.conf import settings
from app.models import Usuario

class U_PasaporteBackend(object):

    def authenticate(self, username=None):
        try:
            user = Usuario.objects.get(username=username)
            if user.has_usable_password():
                return True
            else: 
                return user
        except Usuario.DoesNotExist:
            return "HolaHola"

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None