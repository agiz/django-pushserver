import datetime
import urllib

from django import http
from django.conf import settings
from django.contrib import auth
from django.core import exceptions, urlresolvers
from django.utils.decorators import method_decorator
from django.views import generic as generic_views
from django.views.decorators import csrf
from django.views.generic import simple, edit as edit_views

from pushserver import signals

#from celery.decorators import task

from piplmesh.account import forms, tasks

from celery.task.control import revoke
from celery.worker import state

# http://stackoverflow.com/questions/9769496/celery-received-unregistered-task-of-type-run-example

#@task
#def add(x, y):
#    print "add"
#    return x + y


#@task
#def add(x, y):
#    print("Executing task id %r, args: %r kwargs: %r" % (
#        add.request.id, add.request.args, add.request.kwargs))

class RegistrationView(edit_views.FormView):
    """
    This view checks if form data are valid, saves new user.
    New user is authenticated, logged in and redirected to home page.
    """

    template_name = 'registration.html'
    success_url = urlresolvers.reverse_lazy('home')
    form_class = forms.RegistrationForm

    def form_valid(self, form):
        username, password = form.save()
        new_user = auth.authenticate(username=username, password=password)
        auth.login(self.request, new_user)
        return super(RegistrationView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return simple.redirect_to(request, url=self.get_success_url(), permanent=False)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

class FacebookLoginView(generic_views.RedirectView):
    """ 
    This view authenticates the user via Facebook. 
    """

    permanent = False

    def get_redirect_url(self, **kwargs):
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'scope': settings.FACEBOOK_SCOPE,
            'redirect_uri': self.request.build_absolute_uri(urlresolvers.reverse('facebook_callback')),
        }
        return "https://www.facebook.com/dialog/oauth?%(args)s" % {'args': urllib.urlencode(args)}

class FacebookCallbackView(generic_views.RedirectView):
    """ 
    Authentication callback. Redirects user to LOGIN_REDIRECT_URL. 
    """

    permanent = False
    url = settings.FACEBOOK_LOGIN_REDIRECT

    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            # TODO: Add security measures to prevent attackers from sending a redirect to this url with a forged 'code'
            user = auth.authenticate(token=request.GET['code'], request=request)
            auth.login(request, user)
            # TODO: Message user that they have been logged in (maybe this will already be in auth.login once we move to MongoDB)
            return super(FacebookCallbackView, self).get(request, *args, **kwargs)
        else:
            # TODO: Message user that they have not been logged in because they cancelled the facebook app
            # TODO: Use information provided from facebook as to why the login was not successful
            return super(FacebookCallbackView, self).get(request, *args, **kwargs)

"""
def user_from_session_key(session_key):
    # http://djangosnippets.org/snippets/1276/
    from django.conf import settings
    from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
    from django.contrib.auth.models import AnonymousUser

    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_wrapper = session_engine.SessionStore(session_key)
    session = session_wrapper.load()
    user_id = session.get(SESSION_KEY)
    backend_id = session.get(BACKEND_SESSION_KEY)
    if user_id and backend_id:
        auth_backend = load_backend(backend_id)
        user = auth_backend.get_user(user_id)
        if user:
            return user
    return AnonymousUser()
"""

class PushView(generic_views.TemplateView):
    template_name = 'push.html'

    @method_decorator(csrf.csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PushView, self).dispatch(*args, **kwargs)

    @method_decorator(csrf.csrf_exempt)
    def post(self, request, *args, **kwargs):
        channel_id = request.POST.get('channel_id')

        if not channel_id:
            raise exceptions.PermissionDenied

        #if request.POST.get(signals.SUBSCRIBE_ACTION):
        if request.POST.get('subscribe'):
            print "SUBS", channel_id
            #print request.user.connections

            #action = signals.SUBSCRIBE_ACTION
            request.user.channel[request.POST['channel_id']] = datetime.datetime.now()
            request.user.update(inc__connections=1)
            #request.user.connections = 1

            #print request.user.connections

            #print "ccc0"
            #print request.user.timeout_counter

            # TODO: Cancel timer logout event
            #print request.POST['channel_id']
            #print "ccc"
            #print request.user.timeout_counter
            # TODO: Log out is in progress...
            #if request.user.timeout_counter:
            #    print "revoking..."
            #    print request.user.timeout_counter
            #    revoke(request.user.timeout_counter, terminate=True)
            #    request.user.timeout_counter = None
            #print "cc2"
            #result = tasks.add.delay(16, 4)
            #result = tasks.AsyncResult(request.COOKIES['sessionid'])
            #print result.get()
            #print "..."
            #print tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status

#             if tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'PENDING':
#                 # Task not yet scheduled
#                 print "status: PENDING"
#                 tasks.add.update_state(task_id=request.COOKIES['sessionid'], state='COUNTDOWN')
#             elif tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'COUNTDOWN':
#                 print "status: COUNTDOWN"

            # Reset status
            #tasks.add.update_state(task_id=request.COOKIES['sessionid'], state='PENDING')

            #revoke(request.COOKIES['sessionid'])
#             print 1, tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status
#             print state.revoked
# 
#             if tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'COUNTDOWN' or tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'SUCCESS':
#                 #revoke(request.COOKIES['sessionid'], terminate=True)
#                 revoke(request.COOKIES['sessionid'], terminate=False)
#                 tasks.add.update_state(task_id=request.COOKIES['sessionid'], state='PENDING')
# 
#             print 2, tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status
#             print state.revoked
#             #revoke(request.COOKIES['sessionid'], terminate=True, signal="SIGKILL")
# 
#             #print tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status
#             #result = tasks.add.apply_async(args=[1,2], countdown=10, task_id=request.COOKIES['sessionid'])
#             #result = tasks.add.apply_async(args=[1,2], countdown=10, task_id='a')
#             #result.revoke()
#             #print result
#             #print result.wait()
#             #print result
            print "ddd"
            request.user.save()
        #elif request.POST.get(signals.UNSUBSCRIBE_ACTION):
        elif request.POST.get('unsubscribe'):
            print "UNSU", channel_id
            #print request.user.connections

            #action = signals.UNSUBSCRIBE_ACTION
            request.user.lastaccess = datetime.datetime.now()
            # TODO: Increase connections
            request.user.update(inc__connections=-1)
            #request.user.connections = 1
            

            # TODO: Reset connections
            #request.user.connections = 0

            #print request.user.connections
            #print "end"
            
            #print "aaa"
            #print request.user.timeout_counter
            # TODO: This MUST never cancel UNSUBSCRIBE_ACTION action task!
#             if request.user.timeout_counter:
#                 print "aaanotri"
#                 print request.user.timeout_counter
#                 revoke(request.user.timeout_counter, terminate=True)
#                 request.user.timeout_counter = None
            #print "bb2"

            #print "bb3"
            # TODO: Save task_id and start count down to log out
            #request.user.timeout_counter = tasks.add.apply_async(args=[1,2], countdown=10).__str__()
            #print "bb4"

            # TODO: Fire timer logout event (clear channel from user.channel, logout user)
            #tasks.add.apply_async(args=[1,2])
#             print "aaa"
#             #result = add.delay(4, 4)
#             #print result
#             #result.wait()
#             print 3, tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status
#             print state.revoked
#             if tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'SUCCESS':
#                 tasks.add.update_state(task_id=request.COOKIES['sessionid'], state='PENDING')
# 
#             if tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status == 'PENDING':
#                 tasks.add.update_state(task_id=request.COOKIES['sessionid'], state='COUNTDOWN')
#                 tasks.add.apply_async(args=[1,2], countdown=10, task_id=request.COOKIES['sessionid'])
# 
#             print 4, tasks.add.AsyncResult(task_id=request.COOKIES['sessionid']).status
            print "bbb"
            request.user.save()

        else:
            raise exceptions.PermissionDenied



        print "|"
        #print state.revoked
        #print state.success
        print request.user.connections
        print "|"
        print "\n"

#        if not channel_id and not action:
#            raise exceptions.PermissionDenied



        #from django.contrib.sessions.models import Session
        #from django.contrib.auth.models import User

        #session_key = request.COOKIES['sessionid']
        
        #print Session.objects.get(session_key='0b7c59a9c7d98af94a0df06b70614ad5')

#        session = Session.objects.get(session_key=session_key)
        #uid = session.get_decoded().get('_auth_user_id')
        #user = User.objects.get(pk=uid)
        
        #print uid

        #print user.username, user.get_full_name(), user.email



        #print user_from_session_key(request.COOKIES['sessionid']).gender

        #print request
        #print request.user.lastaccess
        #print request.user.channel
        
#         if action == signals.SUBSCRIBE_ACTION:
#             # TODO: Cancel timer logout event
#             pass
#         elif action == signals.UNSUBSCRIBE_ACTION:
#             request.user.lastaccess = datetime.datetime.now()
#             request.user.save()
#             # TODO: Fire timer logout event
        #elif action == signals.SUBSCRIBE_ACTION and timer_isset:

        
        #print request.COOKIES['sessionid']
        #print request.COOKIES['sessionid'], request.user, channel_id, action

        #signals.passthrough.send_robust(sender=passthrough, request=request, channel_id=channel_id, action=action)

        return http.HttpResponse(status=204)