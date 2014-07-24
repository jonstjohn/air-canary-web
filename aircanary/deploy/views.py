from django.shortcuts import render
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt  
from django.http import HttpResponse

from django.core import serializers

from deploy.models import Push, Deploy
from deploy.utils import deploy_production

class PushView(View):

    def post(self, request, *args, **kwargs):

        import json
        data = json.loads(request.body)

        p = Push()
        p.branch = data['ref']
        p.tag = data['head_commit']['id']
        p.content = request.body
        p.save()

        if data['ref'] == 'refs/heads/master':

            print('Master!!!')

        # TODO - fix this
        import os
        deploy_path = '/home/ac/deploy.sh'
        if os.path.exists(deploy_path):

            deploy_production()
            d = Deploy()
            d.ref = p.branch
            d.rev = p.tag
            d.success = True
            d.save()
        
        return HttpResponse('Groovy')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PushView, self).dispatch(*args, **kwargs)
