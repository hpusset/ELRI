from django.conf import settings

def global_settings(request):
    # return any necessary values
    return {
        'country': settings.COUNTRY,
	'language_code': settings.LANGUAGE_CODE
    }
