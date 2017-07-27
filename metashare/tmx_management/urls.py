from django.conf.urls import patterns, url

urlpatterns = patterns('metashare.tmx_management.views',
                       url(r'^db_info/$', 'db_info'),
                       url(r'^query_language_pair/$', 'get_by_lang_pair'),
                       url(r'^tmx_query/$', 'tmx_query'),
                       )
