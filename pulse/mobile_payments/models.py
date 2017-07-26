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
    crm = models.ForeignKey(CRM)
    provider = models.ForeignKey(MMProvider)
    post = JSONField(name='Mobile money post')
    response = models.CharField(max_length=200)
    def __unicode__(self):              # __str__ on Python 3
        return self.crm.id