# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse

# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import *


from .models import *

#move all the index stuff
def index(request):
    shop_list = Shop.objects.order_by('name')#[:5]
    context = {'shop_list': shop_list}
    return render(request, 'shop/index.html', context)

def shop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    context = {'shop': shop}
    return render(request, 'shop/shop.html', context)

#https://docs.djangoproject.com/en/1.11/topics/forms/


def customer(request, customer_id=None):
    # if this is a POST request we need to process the form data
    if customer_id:
        customer = Customer.objects.get(pk=customer_id)
        title = '%s'%(customer.uid)
        sub_title = '%s %s - state:'%(customer.first,customer.last)
    else:
        customer = None
        title = 'Add New Customer'
        sub_title = ''
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomerForm(request.POST, instance=customer)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            saved = form.save()
            return HttpResponseRedirect(reverse('customer_detail', args=[saved.id]))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CustomerForm(instance=customer)
    context = {'customer': customer, 'form': form, 'title': title,'sub_title':sub_title,'customer_id':customer_id if customer_id else 0}
    return render(request, 'shop/customer.html', context)


def crm(request, crm_id=None):
    # if this is a POST request we need to process the form data
    if crm_id:
        crm = CRM.objects.get(pk=crm_id)
        title = '%s'%(crm.uid)
        sub_title = '%s %s - state: %s'%(crm.customer.first,crm.customer.last, crm.get_state_display())
    else:
        crm = None
        title = 'Add New CRM'
        sub_title = ''
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CRMForm(request.POST, instance=crm)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            saved = form.save()
            return HttpResponseRedirect(reverse('crm_detail', args=[saved.id]))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CRMForm(instance=crm)
    context = {'crm': crm, 'form': form, 'title': title,'sub_title':sub_title,'crm_id':crm_id if crm_id else 0}
    return render(request, 'shop/crm.html', context)



from django_datatables_view.base_datatable_view import BaseDatatableView


class CRMListJson(BaseDatatableView):
    # The model we're going to show
    model = CRM

    # define the columns that will be returned
    columns = ['uid','name','phone','email','state']#, 'user', 'state', 'created', 'modified']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['uid','name','phone','email','state']#, 'user', 'state', '', '']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'name':
            return '{0} {1}'.format(row.first, row.last)
        else:
            return super(CRMListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        #todo filter on shop
        shop_id = self.kwargs.get('shop_id',None)
        if shop_id:
            #table of crm's product history
            qs = qs.filter(shop_id=shop_id)
        #qs = qs.filter(somehow filter on shop_id, what should be linked to a shop?

        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(uid__istartswith=search)


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
        json_data = []
        for item in qs:
            json_data.append([
                "<a href='/shop/crm/%s/'>%s</a>" % (item.id, item.uid),
                "<a href='/shop/customer/%s/'>%s</a>" % (item.customer.id,'{0} {1}'.format(item.customer.first, item.customer.last)),
                item.customer.phone,
                item.customer.email,
                item.state,
            ])
        return json_data



class ShopListJson(BaseDatatableView):
    # The model we're going to show
    model = Shop

    # define the columns that will be returned
    columns = ['name','phone','email','company']#, 'user', 'state', 'created', 'modified']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['name','phone','email','company']#, 'user', 'state', '', '']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        # if column == 'user':
        #     return '{0} {1}'.format(row.crm_firstname, row.crm_lastname)
        #else:
        return super(ShopListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(name__istartswith=search)

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
        json_data = []
        for item in qs:
            json_data.append([
                #item.name,
                "<a href='/shop/%s/'>%s</a>" % (item.id, item.name),
                item.phone,
                item.email,
                item.company.name,
            ])
        return json_data