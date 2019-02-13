from django.conf.urls import url, patterns

urlpatterns = patterns('metashare.stats.views',
  url(r'top/$', 'topstats', name='topstats'),
  url(r'mystats/$', 'mystats', name='mystats'),
  url(r'usage/$', 'usagestats', name='usagestats'),
  url(r'charts/$', 'chartstats', name='chartstats'),
  url(r'charts/tu/$', 'tustats', name='tustats'),
  url(r'charts/groups/$', 'groupsstats', name='groups'),
  url(r'charts/domains/$', 'domainsstats', name='domains'),
  url(r'charts/creation-date/$', 'creationstats', name='creation-dates'),
  url(r'days', 'statdays'),
  url(r'get.*', 'getstats'),
)

