# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse

# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.http import HttpResponseRedirect
from .forms import *


from .models import *
from shop.models import *

import hmac
import urllib
import json

import logging
log = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelformset_factory, formset_factory,inlineformset_factory
#import json

#move all the index stuff
def index(request):
    #shop_list = Shop.objects.order_by('name')#[:5]
    context = {}
    return render(request, 'mobile_payments/index.html', context)

def payment(request,payment_id):
    #shop_list = Shop.objects.order_by('name')#[:5]
    payment = MMPayment.objects.get(pk=payment_id)
    context = {'payment':payment}
    return render(request, 'mobile_payments/payment.html', context)

@csrf_exempt
def payment_post(request):
    '''

    :param request:
    :param payment_id:
    :return:
    '''
    #post comes in

    if request.method == 'POST':
        post_body = json.loads(request.body) #???
        #get mobile money provider AND from that get key to hash against
        provider = MMProvider.objects.get(username=post_body.get('username'),password=post_body.get('password'))
        #match post to a customer with phone number
        key = provider.key
        if ValidateSignature(post_body,key):
            crms = CRM.objects.filter(customer__phone = post_body['sender_phone'])
            if len(crms)==1 and crms[0].state in ['normal','late','downpay']:
                #create the payment
                #the save method on this should do an erp payment creation - and return erpid
                MMPayment.objects.get_or_create(crm=crms[0],provider=provider,post=post_body,reponse='good')
            elif len(crms)==0:
                log.error('No CRMs found with this phone number')
            elif len(crms)>=0:
                log.error('More than one CRM found with this phone number')

        

    return True


def ValidateSignature(post_body,key):
    # base string is the post parameters soreted in ascending order

    # To learn more see https://app.kopokopo.com/push_api
    # set up base string
    try:
        bs = {'account_number': post_body['account_number'], 'amount': post_body['amount'], 'business_number': post_body['business_number'],
              'currency': post_body['currency'],
              'first_name': post_body['first_name'], 'internal_transaction_id': post_body['internal_transaction_id'],
              'last_name': post_body['last_name'], 'middle_name': post_body['middle_name'],
              'sender_phone': post_body['sender_phone'], 'service_name': post_body['service_name'],
              'transaction_reference': post_body['transaction_reference'],
              'transaction_timestamp': post_body['transaction_timestamp'],
              'transaction_type': post_body['transaction_type']}
        base_string = "&".join([k + '=' + urllib.quote_plus(str(bs[k])) for k in sorted(bs)])
    except Exception as e:
        log.error('error hash')
        return True

    try:
        hashed = hmac.new(key, base_string, sha1)
    except Exception as e:
        print 'error hash'
    sSignature = hashed.digest().encode("base64").rstrip('\n')

    # print sSignature + ' = ' + self.signature
    log.error(sSignature + ' = ' + post_body['signature'])
    # print 'base string: ' + base_string
    log.error('base string: ' + base_string)
    # print sSignature == self.signature
    if sSignature == post_body['signature']:
        return True

    return True

from django_datatables_view.base_datatable_view import BaseDatatableView


class PaymentListJson(BaseDatatableView):
    # The model we're going to show
    model = MMPayment

    # define the columns that will be returned
    columns = ['id','crm','provider','post','response']#, 'user', 'state', 'created', 'modified']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id','crm','provider','post','response']#, 'user', 'state', '', '']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'name':
            return '{0} {1}'.format(row.first, row.last)
        else:
            return super(PaymentListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset


        shop_id = self.kwargs.get('shop_id', None)
        # simple example:

        if shop_id:
            #table of crm's product history
            qs = qs.filter(shop_id=shop_id)


        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(erpid__istartswith=search)


            # my custom queries
            # is_vegan = self.request.GET.get(u'is_vegan', None)  # , None)
            # is_veg = self.request.GET.get(u'is_veg', None)
            # is_lacto = self.request.GET.get(u'is_lacto', None)
            # is_gluten = self.request.GET.get(u'is_gluten', None)
            # ethnic = self.request.GET.get(u'ethnic', None)
            # createdbyuser = self.request.GET.get(u'createdbyuser', None)
            # rating = self.request.GET.get(u'rating', None)
            # print rating
            # if is_vegan == 'true':
            #
            #     qs = qs.filter(is_vegan=True)

        # more advanced example using extra parameters
        # filter_crm = self.request.GET.get(u'crm', None)
        #
        # if filter_crm:
        #     crm_parts = filter_crm.split(' ')
        #     qs_params = None
        #     for part in crm_parts:
        #         q = Q(crm_firstname__istartswith=part) | Q(crm_lastname__istartswith=part)
        #         qs_params = qs_params | q if qs_params else q
        #     qs = qs.filter(qs_params)
        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        shop_id = self.kwargs.get('shop_id', None)

        # simple example:

        json_data = []
        for item in qs:
            if 1:#shop_id:
                json_data.append([
                    "<a href='/mobile_payment/payment/%s/'>%s</a>" % (item.id, item.id),
                    "<a href='/shop/crm/%s/'>%s</a>" % (item.id, item.erpid),
                    #"<a href='/shop/customer/%s/'>%s</a>" % (item.customer.id,'{0} {1}'.format(item.customer.first, item.customer.last)),
                    item.provider.name,
                    item.post,
                    item.response,
                ])
        return json_data
