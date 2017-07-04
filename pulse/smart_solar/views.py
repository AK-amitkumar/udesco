# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse

# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from .forms import *
from shop.forms import *


from .models import *
from shop.models import *





def index(request):
    crm_product_list = CRMProduct.objects.order_by('uid')#[:5]
    context = {'crm_product_list': crm_product_list}
    return render(request, 'smart_solar/index.html', context)

def crm_product(request, crm_product_id=None):
    # if this is a POST request we need to process the form data
    if crm_product_id:
        crm_product = CRMProduct.objects.get(pk=crm_product_id)
        title = '%s - %s - %s' % (crm_product.serial_number, crm_product.get_condition_display(),
                                  crm_product.get_enable_state_display())
    else:
        crm_product = None
        title = 'Add New CRMProduct'
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CRMProductForm(request.POST, instance=crm_product)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            saved = form.save()
            return HttpResponseRedirect(reverse('crm_product_detail', args=[saved.id]))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CRMProductForm(instance=crm_product)
    context = {'crm_product': crm_product, 'form': form,
               'title': title,'crm_product_id':crm_product_id if crm_product_id else 0}
    return render(request, 'smart_solar/crm_product.html', context)


from django_datatables_view.base_datatable_view import BaseDatatableView


class CRMProductListJson(BaseDatatableView):
    # The model we're going to show
    model = CRMProduct


    # define the columns that will be returned
    columns = ['product','crm','start_date','enable_state','condition','serial_number','imei','active']#, 'user', 'state', 'created', 'modified']

    order_columns =  ['product','crm','start_date','enable_state','condition','serial_number','imei','active']#, 'user', 'state', '', '']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        # if column == 'user':
        #     return '{0} {1}'.format(row.crm_firstname, row.crm_lastname)
        #else:
        return super(CRMProductListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset
        crm_id = self.kwargs.get('crm_id', None)
        crm_product_id = self.kwargs.get('crm_product_id', None)
        # simple example:
        qs = qs.exclude(serial_number=None)
        if crm_id:
            #table of crm's product history
            qs = qs.filter(crm_id=crm_id)
            self.columns = ['product','start_date','enable_state','condition','serial_number','imei','active']
            self.order_columns = ['product','start_date','enable_state','condition','serial_number','imei','active']
        if crm_product_id:
            #table of history of that crm_product_id
            qs = qs.filter(serial_number=CRMProduct.objects.get(id=crm_product_id).serial_number)
            self.columns = ['crm','start_date','enable_state','condition','active']
            self.order_columns = ['crm','start_date','enable_state','condition','active']

        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(crm__uid__istartswith=search)

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
        crm_id = self.kwargs.get('crm_id', None)
        crm_product_id = self.kwargs.get('crm_product_id', None)


        json_data = []
        for item in qs:
            #['product','crm','start_date','enable_state','condition','serial_number','imei']
            if crm_id:
                json_data.append([
                    # item.name,
                    item.product.name,
                    #"<a href='/shop/crm/%s/'>%s</a>" % (item.crm.id, item.crm.uid),
                    item.start_date,
                    item.enable_state,
                    item.condition,
                    "<a href='/smart_solar/crm_product/%s/'>%s</a>"%(item.id, item.serial_number),
                    item.imei,
                    item.active

                ])
            elif crm_product_id:
                json_data.append([
                    # item.name,
                    #item.product.name,
                    "<a href='/shop/crm/%s/'>%s</a>" % (item.crm.id, item.crm.uid),
                    item.start_date,
                    item.enable_state,
                    item.condition,
                    #"<a href='/smart_solar/crm_product/%s/'>%s</a>" % (item.id, item.serial_number),
                    #item.imei,
                    item.active

                ])
            else:
                json_data.append([
                    # item.name,
                    item.product.name,
                    "<a href='/shop/crm/%s/'>%s</a>" % (item.crm.id, item.crm.uid),
                    item.start_date,
                    item.enable_state,
                    item.condition,
                    "<a href='/smart_solar/crm_product/%s/'>%s</a>" % (item.id, item.serial_number),
                    item.imei,
                    item.active

                ])

        return json_data