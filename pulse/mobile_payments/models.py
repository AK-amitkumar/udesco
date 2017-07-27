# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


import datetime
import json

#for signals
#https://docs.djangoproject.com/en/1.11/ref/signals/#django.db.models.signals.pre_save
from django.db.models.signals import *
from django.dispatch import receiver
import logging
log = logging.getLogger(__name__)
#model signals
    # pre_init
    # post_init
    # pre_save
    # post_save
    # pre_delete
    # post_delete
    # m2m_changed
    # class_prepared
#management signals
    # pre_migrate
    # post_migrate
#Request/response signals
    # request_started
    # request_finished
    # got_request_exception



from bridge import api
from shop.models import *

UID = api.auth_erp()

from django.contrib.postgres.fields import JSONField

# Create your models here.
class MMProvider(models.Model):
    # res_country  in ERP
    name = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    key = models.CharField(max_length=200)#hash key
    # in ERP many other fields, like currency_id
    def __unicode__(self):              # __str__ on Python 3
        return self.name


class MMPayment(models.Model):
    # res_company/res_partner  in ERP
    erpid = models.IntegerField(null=True, blank=True)  # payment id (payment towards invoice)
    crm = models.ForeignKey(CRM)
    provider = models.ForeignKey(MMProvider)
    post_body = models.TextField(verbose_name='Mobile money post')
    response = models.CharField(max_length=200)
    # post_body = JSONField(name='Mobile money post') #This is postgres only todo if I ever go off the sqlite - make this a JSONField
    def __unicode__(self):              # __str__ on Python 3
        return self.crm.id

    def save(self, *args, **kwargs):
        # account.payment.method TABLE
        # "id";"create_uid";"code";"name";"write_uid";"payment_type";"write_date";"create_date"
        # 1;1;"manual";"Manual";1;"inbound";"2017-07-26 17:59:15.865556";"2017-07-26 17:59:15.865556"
        # 2;1;"manual";"Manual";1;"outbound";"2017-07-26 17:59:15.865556";"2017-07-26 17:59:15.865556"
        # 3;1;"electronic";"Electronic";1;"inbound";"2017-07-26 17:59:34.299968";"2017-07-26 17:59:34.299968"
        # 4;1;"check_printing";"Check";1;"outbound";"2017-07-26 18:01:12.018989";"2017-07-26 18:01:12.018989"
        post_body = json.loads(self.post_body)

        amount = post_body.get('amount',0)
        currency = post_body.get('currency',0)
        transaction_timestamp = post_body.get('transaction_timestamp',datetime.datetime.utcnow())
        journal_id = 6 #account.journal type = 'cash' or 'bank' company_id = your company
        fields_dict = {'journal_id':6, 'payment_date':transaction_timestamp, 'currency_id':3, 'amount':amount,
                       'payment_method_id':3, 'payment_type':'inbound', 'partner_id':self.crm.customer.erpid,
                       'partner_type':'customer', 'company_id':self.crm.shop.company.id, #'destination_account_id':None,
                       'invoice_ids':[self.crm.invoice_erpid], 'payment_reference':str(getattr(self, 'crm'))+'mm', 'state':'draft'
                       }
        #state: [('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')]
        # for field in self._meta.get_fields():
        #     # do not write 'id' or foreign key fields to ERP
        #     if not field.is_relation and field.name != 'id':
        #         # cannot write None to the ERP fields
        #         if getattr(self, field.name):
        #             fields_dict[field.name] = getattr(self, field.name)
        if not self.pk:  # overwrite the create() method
            print 'MM Payment created'
            # todo - how the hell do i create payment and apply to invoice???
            # 1. create an account.payment
            erpid = api.create_erp('account.payment', fields_dict)
            if erpid:
                api.function_erp('account.payment', 'post', [erpid],
                                 kwarg_dict={'context': {'active_ids': [erpid]}})
                self.erpid = erpid
                super(MMPayment, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            # todo - probably do not want this type of thing - probably want functions that corresponds to unlink, cancel etc. methods on accoount.invoice
            print 'MM Payment saved'
            api.write_erp('account.payment', [self.erpid], fields_dict)
            super(MMPayment, self).save(*args, **kwargs)  # Call the "real" save() method.