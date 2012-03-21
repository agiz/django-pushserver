import urllib

from django import http
from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.views import generic as generic_views
from django.views.generic import simple
from django.views.generic import edit as form_views

from piplmesh.account import forms

class RegistrationView(form_views.FormView):
    """
    This view checks if form data are valid, saves new user.
    New user is authenticated, logged in and redirected to home page.
    """

    template_name = 'registration.html'
    form_class = forms.RegistrationForm
    success_url = '../'
        
    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        form = forms.RegistrationForm()
        
        context.update({
            'form': form
        })

        return context

    # Overridden method
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return simple.redirect_to(request, url='../', permanent=False)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            username, password = form.save()
            new_user = auth.authenticate(username=username, password=password)
            auth.login(request, new_user)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
class FacebookLoginView(generic_views.RedirectView):
    """ 
    This view authenticates the user via Facebook. 
    """

    permanent = False
    url = 'https://www.facebook.com/dialog/oauth?'
    
    # Overridden method
    def get(self, request, *args, **kwargs):
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'scope': settings.FACEBOOK_SCOPE,
            'redirect_uri': request.build_absolute_uri(reverse('facebook_callback')),
        }
        url = self.get_redirect_url(**kwargs)
        url += urllib.urlencode(args)
        if url:
            if self.permanent:
                return http.HttpResponsePermanentRedirect(url)
            else:
                return http.HttpResponseRedirect(url)
        else:
            logger.warning('Gone: %s' % self.request.path,
                        extra={
                            'status_code': 410,
                            'request': self.request
                        })
            return http.HttpResponseGone() 

class FacebookLogoutView(generic_views.RedirectView):
    """ 
    Log user out of Facebook and redirect to FACEBOOK_LOGOUT_REDIRECT. 
    """

    permanent = False
    url = settings.FACEBOOK_LOGOUT_REDIRECT
    
    # Overridden method
    def get(self, request, *args, **kwargs):
        context = super(FacebookLogoutView, self).get_context_data(**kwargs)
        auth.logout(request)
        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return http.HttpResponsePermanentRedirect(url)
            else:
                return http.HttpResponseRedirect(url)
        else:
            logger.warning('Gone: %s' % self.request.path,
                        extra={
                            'status_code': 410,
                            'request': self.request
                        })
            return http.HttpResponseGone() 

class FacebookCallbackView(generic_views.RedirectView):
    """ 
    Authentication callback. Redirects user to LOGIN_REDIRECT_URL. 
    """

    permanent = False
    url = settings.FACEBOOK_LOGIN_REDIRECT
    
    # Overridden method
    def get(self, request, *args, **kwargs):
        code = request.GET['code']
        user = auth.authenticate(token=code, request=request)
        auth.login(request, user)
        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return http.HttpResponsePermanentRedirect(url)
            else:
                return http.HttpResponseRedirect(url)
        else:
            logger.warning('Gone: %s' % self.request.path,
                        extra={
                            'status_code': 410,
                            'request': self.request
                        })
            return http.HttpResponseGone() 