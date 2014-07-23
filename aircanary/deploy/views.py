from django.shortcuts import render
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt  
from django.http import HttpResponse

from django.core import serializers

from deploy.models import Push

class PushView(View):

    def get(self, request, *args, **kwargs):

        return HttpResponse('')

    def post(self, request, *args, **kwargs):

        import json
        print(request.body)
        obj = json.loads(request.body)

        p = Push()
        p.branch = obj.ref
        p.tag = obj.head
        p.content = request.body
        p.save()

        print(obj)
        return HttpResponse('')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PushView, self).dispatch(*args, **kwargs)
