from django.conf.urls.defaults import patterns, include, url

from django.conf import settings

from piplmesh.account import views as account_views
from piplmesh.frontend import views as frontend_views

urlpatterns = patterns('',
    url('^$', frontend_views.HomeView.as_view(), name='home'),
#    url(r'^(P<slug>)$', frontend_views.HomeView.as_view(), name='home'),

    url(r'^search', frontend_views.SearchView.as_view(), name='search'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^send$', frontend_views.SendView.as_view(), name='send'),
#    url(r'^passthrough', include('pushserver.urls')),
#    url(r'^passthrough', 'piplmesh.frontend.views.process_passthrough', name='process_passthrough'),
#    url(r'^passthrough', frontend_views.PushView.as_view(), name='push'),
    url(r'^passthrough', account_views.PushView.as_view(), name='push'),
#    url(r'^passthrough', 'piplmesh.frontend.views.passthrough', name='pushserver-passthrough'),

    # Registration, login, logout
    url(r'^register/$', account_views.RegistrationView.as_view(), name='registration'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name='logout'),
    # Facebook
    url(r'^facebook/login/$', account_views.FacebookLoginView.as_view(), name='facebook_login'),
    url(r'^facebook/callback/$', account_views.FacebookCallbackView.as_view(), name='facebook_callback'),
)
