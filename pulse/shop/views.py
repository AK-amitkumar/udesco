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
        title = '%s'%(customer.erpid)
        sub_title = '%s'%(customer)
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


def save_crmp_form_fields_to_model(cd,crm,object=None):
    if cd.get('product_id'):
        product_id, qty, serial_number, amount = cd['product_id'], cd['qty'], cd['serial_number'], cd['amount']
        if object:
            object.crm = crm
            object.qty = qty
            object.serial_number = serial_number
            object.amount = amount
            object.product_id = product_id
            object.save()
        else:
            object = CRMProduct.objects.create(crm=crm,qty = qty,serial_number = serial_number,amount = amount,product_id = product_id)
        return object.id
        
def crm(request, crm_id=None):
    # if this is a POST request we need to process the form data
    if crm_id:
        crm = CRM.objects.get(pk=crm_id)
        title = '%s'%(crm.erpid)
        sub_title = '%s %s - state: %s'%(crm.customer.first,crm.customer.last, crm.get_state_display())

        #for the formset
        #for populating the formset
        init_products_info = CRMProduct.objects.filter(crm=crm)
        extra = len(init_products_info) + 1
    else:
        crm = None
        title = 'Add New CRM'
        sub_title = ''

        #for the formset
        extra = 1
        init_products_info = []
    CRMPFormset = formset_factory(CRMProductFormsetLine, can_delete=True, can_order=True, extra=extra)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CRMForm(request.POST, instance=crm)
        formset = CRMPFormset(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            crm = form.save()
        # the following should only happen for crm in draft state
        if 'edit_crm_products' in request.POST or 'action_confirm' in request.POST:
            if formset.is_valid():
                non_deleted_crmp_ids = []
                for form in formset.ordered_forms: #ordered_forms excludes 'DELETE' = True rows
                    cd = form.cleaned_data
                    # if product_id update
                    # if no id, createnew record
                    # if delete flag, delete
                    if cd.get('crm_product_id'):
                        crmp = CRMProduct.objects.get(id = cd['crm_product_id'])
                        #DO not run .update(), because signals will not run
                        save_crmp_form_fields_to_model(cd, crm, object=crmp)
                        non_deleted_crmp_ids.append(cd.get('crm_product_id'))
                    else:#if not cd.get('DELETE'):
                        cr_id = save_crmp_form_fields_to_model(cd, crm)
                        non_deleted_crmp_ids.append(cr_id)
                    #delete the ones marked as DELETE
                delete_products = CRMProduct.objects.filter(crm=crm).exclude(id__in=non_deleted_crmp_ids)
                for p in delete_products:
                    p.delete()
                    #todo call api unlink on the sale_order_id
        # if 'action_confirm' in request.POST:  # Confirm Sale - confirm the sale order
        #     crm.action_confirm()
        #action_confirm now called in action_invoice_create
        elif 'action_invoice_create' in request.POST:  # Create Invoices - create_invoices (when you install)
            crm.action_invoice_create()
        elif 'action_invoice_open' in request.POST:  # Create Invoices - create_invoices (when you install)
            crm.action_invoice_open()
        return HttpResponseRedirect(reverse('crm_detail', args=[crm.id]))

    # if a GET (or any other method) we'll create a blank form
    else:
        formset = CRMPFormset()
        form = CRMForm(instance=crm)
        #===========================
        #populate the empty formset with data from the many2many CRMProduct table
        #===========================
        for i, ingredient_info in enumerate(init_products_info):
            formset[i].fields['crm_product_id'].initial = init_products_info[i].id
            formset[i].fields['product_id'].initial = init_products_info[i].product.id
            formset[i].fields['product_display'].initial = init_products_info[i].product.name
            #todo javascript in crm.html will set the product_id hidden field on select of 'product_display' autocomplete
            #todo javascript will also REset qty=1, serial_number='' on select of 'product_display' autocomplete
            #todo SOME kind of stop if quantity remaining is zero

            #todo - set amount on select of 'product_display' to 1*list_price
            #todo - set amout on select of qty to qty*list_price


            formset[i].fields['qty'].initial = init_products_info[i].qty#['qty']
            formset[i].fields['serial_number'].initial = init_products_info[i].serial_number#['serial_number']
            formset[i].fields['amount'].initial = init_products_info[i].amount#['amount']
    context = {'crm': crm, 'form': form, 'title': title,'formset': formset,
               'sub_title':sub_title,'crm_id':crm_id if crm_id else 0}
    return render(request, 'shop/crm.html', context)




#==================for crm product formset in the crm view
def product_select_options(request):
    json_resp_data = []
    if request.is_ajax():
        products = Product.objects.all()#maybe ignore some
        q = request.GET.get('term', '')
        products = products.filter(default_code__icontains = q )#[:20]#(dispname__icontains = q )[:20]
        for p in products:
            json_resp_data.append({'id':p.id,'label':p.name,'value':p.name})
    return JsonResponse(json_resp_data, safe=False)

@csrf_exempt
def qty_remaining(request):
    #return quantity remaining
    product=Product.objects.get(pk=request.POST['item_id'])
    qty_remaining = product.get_qty_remaining()
    if CRMProduct.objects.filter(product=product).exclude(serial_number=False):
        qty_allowed = 1
    else:
        qty_allowed = qty_remaining if qty_remaining else 99999
    return JsonResponse({'qty_remaining':qty_remaining,'qty_allowed':qty_allowed},safe=False)


def serial_number_select_options(request):
    product_id = request.GET.get('product_id', '')
    json_resp_data = []
    if request.is_ajax():
        #get list of all available CRMProducts
        crm_products = CRMProduct.objects.filter(product_id=product_id,crm=None).exclude(active=False, serial_number=False)#maybe ignore some
        q = request.GET.get('term', '')
        #From these available products, choose a serial number
        crm_products = crm_products.filter(serial_number__icontains = q )#[:20]#(dispname__icontains = q )[:20]
        for p in crm_products:
            json_resp_data.append({'id':p.serial_number,'label':p.serial_number,'value':p.serial_number})
    return JsonResponse(json_resp_data, safe=False)


from django_datatables_view.base_datatable_view import BaseDatatableView


class CRMListJson(BaseDatatableView):
    # The model we're going to show
    model = CRM

    # define the columns that will be returned
    columns = ['erpid','name','phone','email','state']#, 'user', 'state', 'created', 'modified']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['erpid','name','phone','email','state']#, 'user', 'state', '', '']

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


        shop_id = self.kwargs.get('shop_id', None)
        customer_id = self.kwargs.get('customer_id', None)
        # simple example:

        if shop_id:
            #table of crm's product history
            qs = qs.filter(shop_id=shop_id)
        elif customer_id:
            qs = qs.filter(customer_id=customer_id)
        #qs = qs.filter(somehow filter on shop_id, what should be linked to a shop?

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
        customer_id = self.kwargs.get('customer_id', None)
        # simple example:

        json_data = []
        for item in qs:
            if customer_id:
                json_data.append([
                    "<a href='/shop/crm/%s/'>%s</a>" % (item.id, item.erpid),
                    item.state,
                ])
            else: #if shop_id:
                json_data.append([
                    "<a href='/shop/crm/%s/'>%s</a>" % (item.id, item.erpid),
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