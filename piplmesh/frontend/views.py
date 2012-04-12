from django import http
from django.conf import settings
#from django.core import exceptions
from django.views import generic as generic_views
#from django.utils.decorators import method_decorator
#from django.views.decorators import csrf

#from pushserver import signals
from pushserver.utils import updates




"""

from django import dispatch

from pushserver import signals

@dispatch.receiver(signals.passthrough)
def process_passthrough(sender, request, channel_id, action):
    print request.user, channel_id, action

"""


"""
# TODO: Should not be publicly accessible
@csrf.csrf_exempt
def passthrough(request):
    print "pass throught"
    if request.method != 'POST':
        raise exceptions.PermissionDenied

    channel_id = request.POST.get('channel_id')
    if request.POST.get(signals.SUBSCRIBE_ACTION):
        action = signals.SUBSCRIBE_ACTION
    elif request.POST.get(signals.UNSUBSCRIBE_ACTION):
        action = signals.UNSUBSCRIBE_ACTION
    
    if not channel_id and not action:
        raise exceptions.PermissionDenied
        
    #print request
    print request.user, channel_id, action

    signals.passthrough.send_robust(sender=passthrough, request=request, channel_id=channel_id, action=action)

    return HttpResponse(status=204)
"""

from piplmesh.frontend.models import Author
#class HomeView(generic_views.TemplateView):
class HomeView(generic_views.DetailView):
    template_name = 'home.html'
    context_object_name = "publisher"
    model = Author
    
    queryset = Author.objects.all()

    def get_object(self):
        print "get_object"
        object = {'a': '2'}
        return object


    def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super(PublisherDetailView, self).get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         context['book_list'] = Book.objects.all()
        context = {'a': '2'}
        print context
        return context

class SearchView(generic_views.TemplateView):
    template_name = 'search.html'

class SendView(generic_views.TemplateView):
    # TODO: Increase all clients connections!
    template_name = 'send.html'

    def post(self, request, *args, **kwargs):
        print request.META['wsgi.input']._sock.getpeername()
        #print settings.PUSH_SERVER['store']
        #print pushserver

        #print channel.Channel.get_last_message()

        channel_id = 'a'
#        data = {
#            'type': 'answer',
#            'value': 42,
#        }

        data = request.POST['data']
        updates.send_update(channel_id, data)

        return http.HttpResponse(status=204)
"""
class PushView(generic_views.TemplateView):
    template_name = 'send.html'

    @method_decorator(csrf.csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PushView, self).dispatch(*args, **kwargs)

    @method_decorator(csrf.csrf_exempt)
    def post(self, request, *args, **kwargs):
        channel_id = request.POST.get('channel_id')
        if request.POST.get(signals.SUBSCRIBE_ACTION):
            action = signals.SUBSCRIBE_ACTION
        elif request.POST.get(signals.UNSUBSCRIBE_ACTION):
            action = signals.UNSUBSCRIBE_ACTION

        if not channel_id and not action:
            raise exceptions.PermissionDenied

        #print request.COOKIES['sessionid']
        print request.COOKIES['sessionid'], request.user, channel_id, action

        #signals.passthrough.send_robust(sender=passthrough, request=request, channel_id=channel_id, action=action)

        return http.HttpResponse(status=204)
"""