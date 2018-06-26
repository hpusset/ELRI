from metashare.settings import REST_API_KEY
from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized


class RepositoryApiKeyAuthentication(Authentication):
    def _unauthorized(self):
        return HttpUnauthorized()

    def is_authenticated(self, request, **kwargs):

        # superusers and anyone with permission does not need to define an API key
        if request.user.is_superuser or request.user.has_perm('auth.access_api'):
            return True
        # Check for api key if the user is not logged in the repository (e.g. cURL, etc)
        # First check if the key is in the "auth" param
        elif request.GET.get('auth'):
            api_key = request.GET.get('auth').strip()
        # Next check if the key is in the request header
        elif request.META.get('HTTP_AUTHORIZATION'):
            api_key = request.META['HTTP_AUTHORIZATION'].strip()
        # if all above fails, the user is unauthorized
        else:
            return self._unauthorized()

        key_auth_check = self.get_key(api_key)
        return key_auth_check

    def get_key(self, api_key):
        if api_key != REST_API_KEY.strip():
            return self._unauthorized()
        return True
