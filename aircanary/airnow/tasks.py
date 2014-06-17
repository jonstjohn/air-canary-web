from __future__ import absolute_import

from celery import shared_task

from celery.task.schedules import crontab  
from celery.decorators import periodic_task  

# this will run every minute, see http://celeryproject.org/docs/reference/celery.task.schedules.html#celery.task.schedules.crontab  
@periodic_task(run_every=crontab(hour="*", minute="52", day_of_week="*"))  
def grib_periodic():
    from airnow import grib
    grib.run()

@shared_task
def grib_process_csv(param):
    from airnow.grib import AirNowGrib
    a = AirNowGrib()
    a.process_csv(param)

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
