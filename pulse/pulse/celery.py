from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from celery.schedules import crontab

#Import models


import logging
log = logging.getLogger(__name__)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulse.settings')

app = Celery('pulse')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.  in app/tasks.py
app.autodiscover_tasks()


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

# Note run celery like this: $celery -A pulse worker -l info
# or with 'beats' (sheduled tasks) $celery -A pulse beat -l debug
# from helpful article - https://stackoverflow.com/questions/41119053/connect-new-celery-periodic-task-in-django

# quit and restart celery beats
# celery -A pulse worker --events -B -S django -l debug   <------ THIS ONE ACTUALLY RUNS THE PERIODIC TASKS


# celery -A pulse events -l debug --camera django_celery_monitor.camera.Camera --frequency=2


@app.on_after_configure.connect
def periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    # the .s syntax http://docs.celeryproject.org/en/latest/reference/celery.html#celery.signature
    sender.add_periodic_task(5.0, invoice_check.s(1), name='5 Second Invoice Check')


    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     invoice_check.s(),
    # )


@app.task
def invoice_check(args):
    log.info('Celery Scheduled Invoivce Check')
    from shop.models import CRM, Invoice
    from bridge import api
    read_dict_list = api.search_read_erp('account.invoice', [('state','=','draft')],['id','origin'])
    log.info('# of draft invoices = %s'%str(read_dict_list))
    for read_dict in read_dict_list:
        crm_ids = api.search_erp('sale.order', [('name', '=', read_dict['origin'])])
        log.info('SO = %s'%read_dict['origin'])
        if crm_ids:
            # todo only create new draft invoice if customer has paid last invoice
            log.info('Creating Invoice')
            new_draft_invoice = Invoice.objects.get_or_create(erpid=read_dict['id'], crm_id=crm_ids[0])
            log.info('Posting Invoice %s'%new_draft_invoice.id)
            # todo OR MAYBE only post invoice if customer has paid last invoice
            #post invoice and apply payments
            new_draft_invoice.action_invoice_open()
    return True








# from shop.tasks import *
#
# #multiplies (arguments) 2*3 - countdown is when it will run, expires is when the task expires
# mul.apply_async((2,3), countdown=5, expires=10)

