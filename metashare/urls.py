from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from metashare.local_settings import DOCUMENTATION_ROOT
from metashare.repository.editor import admin_site as editor_site
from metashare.repository.sitemap import RepositorySitemap
from metashare.settings import DJANGO_BASE, SITEMAP_URL

urlpatterns = i18n_patterns('',
  url(r'^{0}$'.format(DJANGO_BASE),
    'metashare.views.frontpage', name='frontpage'),
  url(r'^{0}info/$'.format(DJANGO_BASE), TemplateView.as_view(template_name='elri-info.html'), name='info'),
  url(r'^{0}help/$'.format(DJANGO_BASE), TemplateView.as_view(template_name='help.html'), name='help'),
  url(r'^{0}privacy/$'.format(DJANGO_BASE), TemplateView.as_view(template_name='privacy.html'), name='privacy'),
  url(r'^{0}legal/$'.format(DJANGO_BASE), TemplateView.as_view(template_name='legal.html'), name='legal'),
  url(r'^{0}login/$'.format(DJANGO_BASE),
    'metashare.views.login', {'template_name': 'login.html'}, name='login'),
  url(r'^{0}logout/$'.format(DJANGO_BASE), 'metashare.views.logout', name='logout'),

  # url(r'^{0}ecas-login/$'.format(DJANGO_BASE),
  #    'cas.views.login', name='ecas-login'),
  # url(r'^{0}ecas-logout/$'.format(DJANGO_BASE),
  #    'cas.views.logout', {'next_page': '/{0}'.format(DJANGO_BASE)}, name='ecas-logout'),

  url(r'^{0}admin/'.format(DJANGO_BASE),
    include(admin.site.urls)),
  url(r'^{0}editor/'.format(DJANGO_BASE),
    include(editor_site.urls)),
  url(r'^{0}update_subdomains/'.format(DJANGO_BASE),
    'metashare.eurovoc.views.update_subdomains'),
)

urlpatterns += i18n_patterns('metashare.accounts.views',
  (r'^{0}accounts/'.format(DJANGO_BASE), include('metashare.accounts.urls')),
)

urlpatterns += i18n_patterns('metashare.stats.views',
  (r'^{0}stats/'.format(DJANGO_BASE), include('metashare.stats.urls', namespace="statistics")),
)

urlpatterns += i18n_patterns('metashare.repository.views',
  (r'^{0}repository/'.format(DJANGO_BASE), include('metashare.repository.urls')),
)

urlpatterns += i18n_patterns('metashare.sync.views',
  (r'^{0}sync/'.format(DJANGO_BASE), include('metashare.sync.urls')),
)

urlpatterns += i18n_patterns('metashare.bcp47.xhr',
  (r'^{0}bcp47/'.format(DJANGO_BASE), include('metashare.bcp47.urls')),
)

# urlpatterns += patterns('metashare.tmx_management.views',
#   (r'^{0}tmx/'.format(DJANGO_BASE), include('metashare.tmx_management.urls')),
# )

urlpatterns += i18n_patterns('metashare.bcp47.xhr',
  (r'^{0}bcp47/'.format(DJANGO_BASE), include('metashare.bcp47.urls')),
)

urlpatterns += i18n_patterns('',
  (r'^{0}selectable/'.format(DJANGO_BASE), include('selectable.urls')),
)

urlpatterns += i18n_patterns('',
  (r'^{0}documentation/(?P<path>.*)$'.format(DJANGO_BASE), \
        'django.views.static.serve', {'document_root': DOCUMENTATION_ROOT})
)

sitemaps = {
  'site': RepositorySitemap,
}

urlpatterns += i18n_patterns('',
  (r'^{}sitemap\.xml$'.format(DJANGO_BASE), 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

urlpatterns += i18n_patterns('',
  url(r'^{0}progressbarupload/'.format(DJANGO_BASE), include('progressbarupload.urls')),
)

class RobotView(TemplateView):

    def get_context_data(self, **kwargs):
        """ This method is overloaded to pass the SITEMAP_URL into the context data"""
        context = super(RobotView, self).get_context_data(**kwargs)
        context['sitemap_url'] = SITEMAP_URL
        return context

if DJANGO_BASE == "":
    urlpatterns += i18n_patterns('',
    (r'^{}robots\.txt$'.format(DJANGO_BASE), RobotView.as_view(template_name='robots.txt'))
    )

urlpatterns += staticfiles_urlpatterns()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('metashare',),
}

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)
