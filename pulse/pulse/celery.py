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
    # Calls get_newly_generated_draft_invoices
    # the .s syntax http://docs.celeryproject.org/en/latest/reference/celery.html#celery.signature
    sender.add_periodic_task(5.0, get_newly_generated_draft_invoices.s(1), name='get_newly_generated_draft_invoices')


    # Calls update_organization_data
    sender.add_periodic_task(10.0, update_organization_data.s(1), name='update_organization_data')


    # Calls update_product_data
    sender.add_periodic_task(8.0, update_product_data.s(1), name='update_product_data')

    # Calls update_customer_data
    sender.add_periodic_task(20.0, update_customer_data.s(1), name='update_customer_data')




    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     invoice_check.s(),
    # )


@app.task
def get_newly_generated_draft_invoices(args):
    log.info('Celery Scheduled Invoivce Check')
    from shop.models import CRM, Invoice
    from bridge import api
    read_dict_list = api.search_read_erp('account.invoice', [('state','=','draft')],['id','origin'])
    log.info('# of draft invoices = %s'%len(read_dict_list))
    for read_dict in read_dict_list:
        log.info(read_dict)
        crm_ids = api.search_erp('sale.order', [('name', '=', read_dict['origin'])])
        log.info('SO = %s'%read_dict['origin'])
        if crm_ids:
            # todo only create new draft invoice if customer has paid last invoice
            log.info('Creating Invoice')
            new_draft_invoice, cr = Invoice.objects.get_or_create(erpid=read_dict['id'], crm_id=crm_ids[0])
            log.info('call action_invoice_open() on invoice %s'%new_draft_invoice.id)
            # todo OR MAYBE only post invoice if customer has paid last invoice
            #post invoice and apply payments
            new_draft_invoice.action_invoice_open()
    return True


@app.task
def update_organization_data(args):
    log.info('Celery Scheduled Update Organization')

    from bridge import demo
    demo.get_countries()
    demo.get_companies()
    demo.get_suppliers()

    return True


@app.task
def update_product_data(args):
    log.info('Celery Scheduled Update Products')

    from bridge import demo
    demo.get_products()

    return True


@app.task
def update_customer_data(args):
    log.info('Celery Scheduled Update Customers')

    from bridge import demo
    demo.get_customers()

    return True


#
# [2017-07-29 22:09:38,248: INFO/ForkPoolWorker-3] Celery Scheduled Invoivce Check
# [2017-07-29 22:09:38,271: INFO/ForkPoolWorker-3] # of draft invoices = 2
# [2017-07-29 22:09:38,271: INFO/ForkPoolWorker-3] {'origin': 'SO139', 'id': 48}
# [2017-07-29 22:09:38,284: INFO/ForkPoolWorker-3] SO = SO139
# [2017-07-29 22:09:38,285: INFO/ForkPoolWorker-3] Creating Invoice
# [2017-07-29 22:09:38,312: INFO/ForkPoolWorker-3] Invoice object
# [2017-07-29 22:09:38,797: ERROR/ForkPoolWorker-3] Task pulse.celery.invoice_check[c423d2d3-579a-41b9-9adf-199ec4197390] raised unexpected: Error()
# Traceback (most recent call last):
#   File "/home/aiden/udesco/venv/local/lib/python2.7/site-packages/celery/app/trace.py", line 374, in trace_task
#     R = retval = fun(*args, **kwargs)
#   File "/home/aiden/udesco/venv/local/lib/python2.7/site-packages/celery/app/trace.py", line 629, in __protected_call__
#     return self.run(*args, **kwargs)
#   File "/home/aiden/udesco/pulse/pulse/celery.py", line 75, in invoice_check
#     new_draft_invoice.action_invoice_open()
#   File "/home/aiden/udesco/pulse/shop/models.py", line 287, in action_invoice_open
#     aml_ids = api.function_erp('account.invoice', '_get_outstanding_account_move_lines', [self.erpid])
#   File "/home/aiden/udesco/pulse/bridge/api.py", line 318, in function_erp
#     arg_list, kwarg_dict)
#   File "/usr/lib/python2.7/xmlrpclib.py", line 1243, in __call__
#     return self.__send(self.__name, args)
#   File "/usr/lib/python2.7/xmlrpclib.py", line 1602, in __request
#     verbose=self.__verbose
#   File "/usr/lib/python2.7/xmlrpclib.py", line 1283, in request
#     return self.single_request(host, handler, request_body, verbose)
#   File "/usr/lib/python2.7/xmlrpclib.py", line 1316, in single_request
#     return self.parse_response(response)
#   File "/usr/lib/python2.7/xmlrpclib.py", line 1493, in parse_response
#     return u.close()
#   File "/usr/lib/python2.7/xmlrpclib.py", line 800, in close
#     raise Fault(**self._stack[0])
# Fault: Error()







# from shop.tasks import *
#
# #multiplies (arguments) 2*3 - countdown is when it will run, expires is when the task expires
# mul.apply_async((2,3), countdown=5, expires=10)

