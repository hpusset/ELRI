from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class ApiDjangoAuthorization(Authorization):

    READ_PERM_CODE = 'access'  # matching respective Permission.codename

    def create_list(self, object_list, bundle):
        pass

    def read_list(self, object_list, bundle):
        # now we check here for specific permission
        if not bundle.request.user.has_perm('auth.access_api'):
            raise Unauthorized("You are not allowed to access that resource.")
        result = super(ApiDjangoAuthorization, self).read_list(object_list, bundle)
        return result

    def read_detail(self, object_list, bundle):
        # now we check here for specific permission
        if not bundle.request.user.has_perm('auth.access_api'):
            raise Unauthorized("You are not allowed to access that resource.")
        result = super(ApiDjangoAuthorization, self).read_detail(object_list, bundle)
        return result
