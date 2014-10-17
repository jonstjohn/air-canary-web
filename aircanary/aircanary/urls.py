from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from places.views import MobileView, DesktopView, ComingView, CompareView
from deploy.views import PushView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aircanary.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('places.views',
    url(r'^$', ComingView.as_view(), name='coming'),
    url(r'^m$', MobileView.as_view(), name='mobile'),
    url(r'^d$', DesktopView.as_view(), name='desktop'),
    url(r'^gitpush$', PushView.as_view(), name='gitpush'),
    url(r'^compare$', CompareView.as_view(), name='compare'), 
)
