import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from lib.Notifier import notify


@csrf_exempt
def token_handle(request):
    notify(str(json.loads(request.body.decode('utf-8'))))
    return HttpResponse('Salamaleykum')
