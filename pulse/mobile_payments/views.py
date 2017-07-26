# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse

# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.http import HttpResponseRedirect
from .forms import *


from .models import *

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
