from django.shortcuts import render
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt  
from django.http import HttpResponse

from django.core import serializers

from deploy.models import Push

class PushView(View):

    def post(self, request, *args, **kwargs):

        import json
        data = json.loads(request.body)

        p = Push()
        p.branch = data['ref']
        p.tag = data['head_commit']['id']
        p.content = request.body
        p.save()

        if data['ref'] == 'refs/head/master':

            print('Master!!!')

        return HttpResponse('Groovy')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PushView, self).dispatch(*args, **kwargs)
