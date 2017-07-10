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
        title = '%s'%(crm.erpid)
        sub_title = '%s %s - state: %s'%(crm.customer.first,crm.customer.last, crm.get_state_display())

        #for the formset
        extra = len(crm.crm_products.all()) + 1
    else:
        crm = None
        title = 'Add New CRM'
        sub_title = ''

        #for the formset
        extra = 1

    CRMPFormset = formset_factory(CRMProductFormsetLine, can_delete=True, can_order=True, extra=extra)
    if request.method == 'POST':
        formset=CRMPFormset(request.POST, request.FILES)
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
        formset = CRMPFormset()
        form = CRMForm(instance=crm)
    context = {'crm': crm, 'form': form, 'title': title,'formset': formset,
               'sub_title':sub_title,'crm_id':crm_id if crm_id else 0}
    return render(request, 'shop/crm.html', context)

#  CRMProductFormsetLine

#
# def recipe(request, id=None):
#     recipe_nutrients = []
#     ingredients_list = []
#     if id:
#         recipe = Recipe.objects.get(id=id)
#         init_ingredients_info = recipe.ingredients
#         init_nutrients_info = recipe.nuts
#         #whole chart
#         #chart_labels = [n.get('name') for n in init_nutrients_info if n.get('val') >= 0.001]
#         #chart_data = [n.get('val') for n in init_nutrients_info if n.get('val') >= 0.001]
#         #Proximates, Lipids, Vitamins, Minerals, Other
#         prox_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Proximates')]
#         prox_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Proximates')]
#         lip_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Lipids')]
#         lip_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Lipids')]
#         vit_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Vitamins')]
#         vit_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Vitamins')]
#         min_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Minerals')]
#         min_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Minerals')]
#         oth_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Other')]
#         oth_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Other')]
#         extra = len(init_ingredients_info)+1
#     else:
#         recipe = None
#         init_ingredients_info, init_nutrients_info = [],[]
#         prox_labels, prox_data, lip_data, lip_labels, vit_labels, vit_data, min_labels, min_data, oth_labels, oth_data= \
#         [],[],[],[],[],[],[],[],[],[]
#         extra = 1
#     IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True, extra = extra)
#     if request.method == 'POST':
#         formset = IngredientsFormSet(request.POST, request.FILES)
#         rform = RecipeForm(request.POST)
#         if formset.is_valid() and rform.is_valid():
#             #EACH FORM = RECIPE ITEM
#             for form in formset.ordered_forms:
#                 recipe = rform.save(commit=False) #do not commit twice
#                 cd = form.cleaned_data
#                 food, units, amt = cd['food'], cd['units'], cd['amt']
#                 choices = Food.objects.get(name=cd['food']).get_units_choices()
#                 ingredients_list.append({'food':food, 'units':units, 'amt':amt, 'choices':choices})
#                 single_food_nutrients = Food.objects.get(name = food).nuts
#                 #first iteration hits Water
#                 for nut_dict in single_food_nutrients:
#                     nut_name = nut_dict['name'] if nut_dict['name'] != 'Energy' else '%s (%s)'%(nut_dict['name'],nut_dict['unit'])#Water, Fat, etc.
#                     nut_unit = nut_dict['unit']#gram or microgram - make sure these are consistent between DIFFERENT FOODS
#                     nut_group = nut_dict['group'] #Proximates, Lipids, Vitamins, Minerals, Other
#                     #EQUIVALENT output - which is faster?
#                     #see speed_test.txt
#                     matching_measure = [n for n in nut_dict['measures'] if n.get('label') == units]
#                     #matching_measure = filter(lambda n: n.get('label') == units, nut_dict['measures'])
#                     if matching_measure:
#                         nut_serving_val = matching_measure[0]['value']
#                     else:
#                         nut_serving_val = nut_dict['value']
#                     nut_val = nut_serving_val * amt #total - measures * amt
#                     #EQUIVALENT
#                     recipe_nutrient = [n for n in recipe_nutrients if (n.get('name') == nut_name and n.get('unit') == nut_unit)]
#                     #recipe_nutrient = filter(lambda n: (n.get('name') == nut_name and n.get('unit') == nut_unit), recipe_nutrients)
#                     if not recipe_nutrient: #update list with new nutrient
#                         recipe_nutrients.append({'name':nut_name, 'unit':nut_unit, 'val':nut_val, 'group':nut_group})
#                     else:
#                         #weirdly enough this works, updating 'a' in a dictionary
#                         #in a filtered_list = [{'a':x}] updates 'a' in original list [{'a':x}, {'b':y}]
#                         recipe_nutrient[0]['val'] = recipe_nutrient[0]['val'] + nut_val
#             recipe.ingredients = ingredients_list
#             recipe.nuts = recipe_nutrients
#             recipe.save()
#             return HttpResponseRedirect(reverse('recipe', args=(recipe.id,)))#HttpResponse([recipe.nuts, recipe.ingredients])
#         else:
#             return HttpResponse(formset.errors)
#     else:
#         rform = RecipeForm(instance = recipe)
#         formset = IngredientsFormSet() #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
#         for i,ingredient_info in enumerate(init_ingredients_info):
#             #get recipe nuts['ingredients']
#             #this ok - recipe only called if forloop hits
#             units_choices = init_ingredients_info[i]['choices']
#             #choices_tuple = ((k, k) for k in choices_list)
#             formset[i].fields['units'].choices = units_choices#(('cup', 'cup'),('serving', 'serving'))#init_ingredients_info[i]['choices']
#             formset[i].fields['units'].initial = init_ingredients_info[i]['units']
#             formset[i].fields['amt'].initial = init_ingredients_info[i]['amt']#this actually needs to be set from recipe.nuts
#             formset[i].fields['food'].initial = init_ingredients_info[i]['food']#
#     return render(request, 'app/recipe.html', {'rform':rform,'formset': formset,
#                                                'nutrients':init_nutrients_info,
#                                                'prox_labels':json.dumps(prox_labels),
#                                                'prox_data':json.dumps(prox_data),
#                                                'lip_labels':json.dumps(lip_labels),
#                                                'lip_data':json.dumps(lip_data),
#                                                'vit_data':json.dumps(vit_data),
#                                                'vit_labels':json.dumps(vit_labels),
#                                                'min_data':json.dumps(min_data),
#                                                'min_labels':json.dumps(min_labels),
#                                                'oth_labels':json.dumps(oth_labels),
#                                                'oth_data':json.dumps(oth_data),
#                                                                        }) #use this to get the nutritional facts and data for charts

























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
    return JsonResponse(qty_remaining,safe=False)


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

        #todo filter on shop
        shop_id = self.kwargs.get('shop_id',None)
        if shop_id:
            #table of crm's product history
            qs = qs.filter(shop_id=shop_id)
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
        json_data = []
        for item in qs:
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