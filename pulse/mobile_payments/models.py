# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


import datetime

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
        fields_dict = {}
        for field in self._meta.get_fields():
            # do not write 'id' or foreign key fields to ERP
            if not field.is_relation and field.name != 'id':
                # cannot write None to the ERP fields
                if getattr(self, field.name):
                    fields_dict[field.name] = getattr(self, field.name)
                #todo - how the hell do i create payment and apply to invoice???
                # fields_dict['order_id'] = self.crm.erpid
                # fields_dict['product_id'] = self.product.product_erpid
        if not self.pk:  # overwrite the create() method
            print 'MM Payment created'
            #erpid = api.create_erp('sale.order.line', fields_dict)
            # don't save if no erpid is returned
            # if erpid:
            #     self.erpid = erpid
            #     super(MMPayment, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            print 'MM Payment saved'
            api.write_erp('sale.order.line', [self.erpid], fields_dict)
            super(MMPayment, self).save(*args, **kwargs)  # Call the "real" save() method.