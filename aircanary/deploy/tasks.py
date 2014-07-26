from __future__ import absolute_import

from celery import shared_task

@shared_task
def deploy_prod(param):
    """ Deploy to production """
    from deploy.utils import deploy_prod
    deploy_prod()
