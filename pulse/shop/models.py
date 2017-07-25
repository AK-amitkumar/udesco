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

UID = api.auth_erp()



# Create your models here.
class Country(models.Model):
    # res_country  in ERP
    code = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    # in ERP many other fields, like currency_id
    def __unicode__(self):              # __str__ on Python 3
        return self.code


class Company(models.Model):
    # res_company/res_partner  in ERP
    erpid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    country = models.ForeignKey('Country')
    def __unicode__(self):              # __str__ on Python 3
        return self.name




class Shop(models.Model):
    #no corresponding model in erp yet
    name = models.CharField(max_length=200) #first and last
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200)
    country = models.ForeignKey('Country',null=True, blank=True) #should default to company
    company = models.ForeignKey('Company')
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200)
    payg = models.BooleanField(default=False)  # is it a PAYG payment model
    def __unicode__(self):              # __str__ on Python 3
        return self.name


class Customer(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    erpid = models.IntegerField(null=True, blank=True) #Unique CustomerId
    first = models.CharField(max_length=200, null=True, blank=True)  # first
    last = models.CharField(max_length=200, null=True, blank=True)  # last
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200, null=True, blank=True)
    country = models.ForeignKey('Country', null=True, blank=True)
    #shop = models.ForeignKey('Shop') on the crm
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    def __unicode__(self):  # __str__ on Python 3
        return self.first+' '+self.last

    def save(self, *args, **kwargs):
        fields_dict = {}
        # fields = api.inspect_erp('res.partner')
        for field in self._meta.get_fields():
            # do not write 'id' or foreign key fields to ERP
            if not field.is_relation and field.name != 'id':
                # cannot write None to the ERP fields
                if getattr(self, field.name):
                    fields_dict[field.name] = getattr(self, field.name)
        fields_dict['name'] = fields_dict.get('first', '') + ' ' + fields_dict.get('last', '')
        if not self.pk:  # overwrite the create() method
            fields_dict['customer'] = True
            erpid = api.create_erp('res.partner', fields_dict)
            # don't save if no erpid is returned
            if erpid:
                self.erpid = erpid
                super(Customer, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            api.write_erp('res.partner', [self.erpid], fields_dict)
            super(Customer, self).save(*args, **kwargs)  # Call the "real" save() method.

class Supplier(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    erpid = models.IntegerField(null=True, blank=True)  # Unique CRM Id
    name = models.CharField(max_length=200)  # first and last
    # shop = models.ForeignKey('Shop') # linked through the invoice, not the shop
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200)
    country = models.ForeignKey('Country')
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):  # __str__ on Python 3
        return self.name




PAYMENT_STATE = (('draft','Draft'),('downpay','Downpay'),('late','Late'),('normal','Normal'),('defaulted','Defaulted'),('repo','Repossessed'))

class CRM(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    # creation of crm chould only happen on creation of crm products - and this should generate sale order
    erpid = models.IntegerField(null=True, blank=True) #Unique CRM Id
    shop = models.ForeignKey('Shop') # linked through the invoice, not the shop
    customer = models.ForeignKey('Customer')
    state = models.CharField(max_length=200, choices = PAYMENT_STATE, default = 'draft')
    crm_products = models.ManyToManyField('Product', through='CRMProduct', null=True, blank=True)
    payg = models.NullBooleanField(null=True, blank=True)  # is it a PAYG payment model - inherits from shop
    def __unicode__(self):  # __str__ on Python 3
        return str(self.erpid)
    # def action_confirm(self):
    def save(self, *args, **kwargs):
        fields_dict = {}
        for field in self._meta.get_fields():
            # do not write 'id' or foreign key fields to ERP
            if not field.is_relation and field.name != 'id':
                # cannot write None to the ERP fields
                if getattr(self, field.name):
                    fields_dict[field.name] = getattr(self, field.name)
        if not self.pk:  # overwrite the create() method
            fields_dict['partner_id'] = self.customer.erpid #the customer
            erpid = api.create_erp('sale.order', fields_dict)
            # don't save if no erpid is returned
            if erpid:
                self.erpid = erpid
                super(CRM, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            api.write_erp('sale.order', [self.erpid], fields_dict)
            super(CRM, self).save(*args, **kwargs)  # Call the "real" save() method.
    # todo SAVE the CRMProduct - should be a  sale.order.line (sale_order.order_line)
    def action_confirm(self):
        api.function_erp('sale.order', 'action_confirm', [self.erpid])
    def action_invoice_create(self):#'action_invoice_create' in kwargs:
        #api.function_erp('sale.advance.payment.inv', 'create_invoices', [self.erpid], kwarg_dict = {'context':{'active_ids':[self.erpid]}})
        #NOTE self.erpid = sale_order_id
        #sale_order_to_invoice_data = [self.erpid, {'context': {'active_ids': self.erpid}}]
        api.function_erp('sale.order', 'action_invoice_create', [self.erpid], kwarg_dict = {'context':{'active_ids':[self.erpid]}})





#https://www.odoo.com/documentation/user/9.0/inventory/settings/products/variants.html
#http://odoo-development.readthedocs.io/en/latest/odoo/models/product.template.html
# The stores have products that differ from some other only a one or few properties.
# Such goods it makes no sense to separate as individual products.
# They are join in a group of similar goods, which are called template.
# shop: product pages use product.template (when order is created, then product.product is used).


PRODUCT_TYPE = (('service','Service'),('stock','Stockable'),('consu','Consumable'))
class Product(models.Model):
    # product_product - is a product 'variant' of product.template - when you create an order, order line has fk to this
    # procuct_template - product_product has a fk to this - this is where most of the product info is

    # so what should happen is this model should be more like a product_template
    erpid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    default_code = models.CharField(max_length=200)# not unique in ERP, use erpid for identification
    list_price = models.FloatField(default=0)
    type = models.CharField(max_length=200, choices=PRODUCT_TYPE,null=True,blank=True)
    def __unicode__(self):  # __str__ on Python 3
        return self.default_code
    def save(self, *args, **kwargs):
        fields_dict = {}
        # fields = api.inspect_erp('res.partner')
        for field in self._meta.get_fields():
            # do not write 'id' or foreign key fields to ERP
            if not field.is_relation and field.name != 'id':
                # cannot write None to the ERP fields
                if getattr(self, field.name):
                    fields_dict[field.name] = getattr(self, field.name)
        fields_dict['name'] = fields_dict.get('name', '') + ' ' + fields_dict.get('last', '')
        if not self.pk:  # overwrite the create() method
            erpid = api.create_erp('product.template', fields_dict)
            # don't save if no erpid is returned
            if erpid:
                self.erpid = erpid
                super(Product, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            api.write_erp('product.template', [self.erpid], fields_dict)
            super(Product, self).save(*args, **kwargs)  # Call the "real" save() method.

    def get_qty_remaining(self,*args,**kwargs):
        #get qty remaining from the erp somehow
        return 100



ENABLE_STATE = (('enabled','Enabled'),('disabled','Disabled'))
CONDITION = (('normal','Normal'),('damaged','Damaged'))

class CRMProduct(models.Model):
    '''
    
    CRMProduct is many to many between CRM (customers account - which they are invoiced for)
    and Product (corresponds to product.template)
    
    In some ways the CRMProduct is like invoice line or sale order line in that it takes product unit_price * qty = amt
    and the CRM, which corresponds to a sale order and later to the invoice has CRMProducts for 'lines'
     
     In other ways it is similar to a Product or whatever you would call it in smart solar
     CRMProducts of certain product types will have a serial number and max quantity of 1
     Some products will have no serial number and multiple quantity is possible
    
    
    
    '''
    # each line here should roll up to an sale_order_line - not account_invoice_line
    erpid = models.IntegerField(null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE) #corresponds to product_product
    crm = models.ForeignKey('CRM', on_delete=models.CASCADE, null=True, blank=True)
    #account_id - income or expense account
    start_date = models.DateTimeField(default = datetime.datetime.utcnow())
    end_date = models.DateTimeField(null=True, blank=True)
    enable_state = models.CharField(max_length=200, choices=ENABLE_STATE, default = 'disabled')
    condition = models.CharField(max_length=200, choices=CONDITION, default = 'normal')
    #price = models.FloatField()
    #tax set in ERP
    #amount - calculated from qty, price and tax - in ERP
    serial_number = models.CharField(max_length=200, null=True, blank=True)#unique=True) only on control unit
    imei = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True) # does crm have product
    price_unit = models.FloatField(null=True, blank=True) # at time of install
    qty = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True) #set in the crm.html javascript
    # def amount(self):  # __str__ on Python 3
    #     qty = self.qty if self.qty else 0
    #     price_unit = self.price_unit if self.price_unit else 0
    #     return price_unit * qty
    def __unicode__(self):  # __str__ on Python 3
        return '%s, %s'%(self.product.default_code,self.serial_number)

    def unlink(self):
        #Unlink from a customer
        self.crm=None
        self.save() #do i need to super or something?

    def return_product_choices(self):
        #((k, k) for k in choices_list)
        return [(self.id, self.product.name),]#{'id': self.id, 'label': self.product.name, 'value': self.product.name}

    def save(self, *args, **kwargs):
        fields_dict = {}
        for field in self._meta.get_fields():
            # do not write 'id' or foreign key fields to ERP
            if not field.is_relation and field.name != 'id':
                # cannot write None to the ERP fields
                if getattr(self, field.name):
                    fields_dict[field.name] = getattr(self, field.name)
                fields_dict['product_uom_qty'] = self.qty if self.qty else 1
                #fields_dict['price_unit'] = self.price_unit
                fields_dict['order_id'] = self.crm.erpid
                fields_dict['product_id'] = self.product.erpid
                #todo self.product.erpid is the id of the product_template, BUT 'product_id' is a link to product.product model
        if not self.pk:  # overwrite the create() method
            print 'CRMP created'
            erpid = api.create_erp('sale.order.line', fields_dict)
            # don't save if no erpid is returned
            if erpid:
                self.erpid = erpid
                super(CRMProduct, self).save(*args, **kwargs)
        else:  # overwrite the save() method
            print 'CRMP saved'
            api.write_erp('sale.order.line', [self.erpid], fields_dict)
            super(CRMProduct, self).save(*args, **kwargs)  # Call the "real" save() method.









# class Employee(models.Model):
#     # hr_employee/res_partner
#     # in ERP hr_employee.adress_id is a many2one to res_partner
#     name = models.CharField(max_length=200)
#     shop = models.ForeignKey('Shop')
# 
#     def __unicode__(self):  # __str__ on Python 3
#         return self.name

# INVOICE_STATES = (
#     ('draft', 'draft'),
#     ('proforma', 'proforma'),
#     ('proforma2', 'proforma2'),
#     ('open', 'open'),
#     ('paid', 'paid'),
#     ('cancel', 'cancel'),
# )
#

#
# #This should probably be a many to many field with Product and Invoice
# class InvoiceLine(models.Model):
#     # account_invoice_line
#     product = models.ForeignKey('Product', on_delete=models.CASCADE) #corresponds to product_product
#     invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
#     #account_id - income or expense account
#     qty = models.FloatField()
#     #price = models.FloatField()
#     #tax set in ERP
#     #amount - calculated from qty, price and tax - in ERP
#     #serial_number = models.CharField(max_length=200)
#     #imei = models.CharField(max_length=200)


#
#
#     AutoField
#     BigAutoField
#     BigIntegerField
#     BinaryField
#     BooleanField
#     CharField
#     CommaSeparatedIntegerField
#     DateField
#     DateTimeField
#     DecimalField
#     DurationField
#     EmailField
#     FileField
#         FileField and FieldFile
#     FilePathField
#     FloatField
#     ImageField
#     IntegerField
#     GenericIPAddressField
#     NullBooleanField
#     PositiveIntegerField
#     PositiveSmallIntegerField
#     SlugField
#     SmallIntegerField
#     TextField
#     TimeField
#     URLField
#     UUIDField
#
# Relationship fields
#
#     ForeignKey
#         Database Representation
#         Arguments
#     ManyToManyField
#         Database Representation
#         Arguments
#     OneToOneField

