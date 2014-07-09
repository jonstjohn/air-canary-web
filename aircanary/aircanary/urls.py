from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from places.views import HomeView, DesktopView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aircanary.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('places.views',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^d$', DesktopView.as_view(), name='desktop')
)
