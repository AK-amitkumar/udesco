# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import datetime

#for signals
#https://docs.djangoproject.com/en/1.11/ref/signals/#django.db.models.signals.pre_save
from django.db.models.signals import *
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


# Create your models here.



class Shop(models.Model):
    # res_partner in ERP
    name = models.CharField(max_length=200) #first and last
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200)
    country = models.ForeignKey('Country',null=True, blank=True) #should default to company
    company = models.ForeignKey('Company')
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200)
    parent = models.ForeignKey('Shop', null=True, blank=True)
    payg = models.BooleanField(default=False)  # is it a PAYG payment model
    def __unicode__(self):              # __str__ on Python 3
        return self.name

class Company(models.Model):
    # res_company/res_partner  in ERP
    name = models.CharField(max_length=200)
    country = models.ForeignKey('Country')
    def __unicode__(self):              # __str__ on Python 3
        return self.name


class Country(models.Model):
    # res_country  in ERP
    code = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    # in ERP many other fields, like currency_id
    def __unicode__(self):              # __str__ on Python 3
        return self.code


class Employee(models.Model):
    # hr_employee/res_partner
    # in ERP hr_employee.adress_id is a many2one to res_partner
    name = models.CharField(max_length=200)
    shop = models.ForeignKey('Shop')
    def __unicode__(self):              # __str__ on Python 3
        return self.name


class Customer(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    uid = models.CharField(max_length=200, unique= True) #Unique CustomerId
    first = models.CharField(max_length=200, null=True, blank=True)  # first
    last = models.CharField(max_length=200, null=True, blank=True)  # last
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200, null=True, blank=True)
    country = models.ForeignKey('Country', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    def __unicode__(self):  # __str__ on Python 3
        return self.uid


PAYMENT_STATE = (('draft','Draft'),('downpay','Downpay'),('late','Late'),('normal','Normal'),('defaulted','Defaulted'),('repo','Repossessed'))

class CRM(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    # creation of crm chould only happen on creation of crm products - and this should generate sale order
    uid = models.CharField(max_length=200, unique= True) #Unique CRM Id
    shop = models.ForeignKey('Shop') # linked through the invoice, not the shop
    customer = models.ForeignKey('Customer')
    state = models.CharField(max_length=200, choices = PAYMENT_STATE, default = 'draft')
    crm_products = models.ManyToManyField('Product', through='CRMProduct', null=True, blank=True)
    payg = models.NullBooleanField(null=True, blank=True)  # is it a PAYG payment model - inherits from shop
    def __unicode__(self):  # __str__ on Python 3
        return self.uid


class Supplier(models.Model):
    # res_partner of crm = True  // alternative is supplier = True
    name = models.CharField(max_length=200) #first and last
    #shop = models.ForeignKey('Shop') # linked through the invoice, not the shop
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street2 = models.CharField(max_length=200, null=True, blank=True)
    zip = models.CharField(max_length=200)
    country = models.ForeignKey('Country')
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    def __unicode__(self):  # __str__ on Python 3
        return self.name



#https://www.odoo.com/documentation/user/9.0/inventory/settings/products/variants.html
#http://odoo-development.readthedocs.io/en/latest/odoo/models/product.template.html
# The stores have products that differ from some other only a one or few properties.
# Such goods it makes no sense to separate as individual products.
# They are join in a group of similar goods, which are called template.
# shop: product pages use product.template (when order is created, then product.product is used).

class Product(models.Model):
    # product_product - is a product 'variant' of product.template - when you create an order, order line has fk to this
    # procuct_template - product_product has a fk to this - this is where most of the product info is

    # so what should happen is this model should be more like a product_template
    name = models.CharField(max_length=200)
    default_code = models.CharField(max_length=200, unique = True)
    list_price = models.FloatField(default=0)
    def __unicode__(self):  # __str__ on Python 3
        return self.default_code



ENABLE_STATE = (('enabled','Enabled'),('disabled','Disabled'))
CONDITION = (('normal','Normal'),('damaged','Damaged'))

class CRMProduct(models.Model):
    # each line here should roll up to an sale_order_line - not account_invoice_line
    product = models.ForeignKey('Product', on_delete=models.CASCADE) #corresponds to product_product
    crm = models.ForeignKey('CRM', on_delete=models.CASCADE)
    #account_id - income or expense account
    start_date = models.DateTimeField(default = datetime.datetime.utcnow())
    end_date = models.DateTimeField(null=True, blank=True)
    enable_state = models.CharField(max_length=200, choices=ENABLE_STATE, default = 'disabled')
    condition = models.CharField(max_length=200, choices=CONDITION, default = 'normal')
    #price = models.FloatField()
    #tax set in ERP
    #amount - calculated from quantity, price and tax - in ERP
    serial_number = models.CharField(max_length=200, null=True, blank=True)#unique=True) only on control unit
    imei = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True) # does crm have product
    price_unit = models.FloatField(null=True, blank=True) # at time of install
    quantity = models.FloatField(null=True, blank=True)
    def amount(self):  # __str__ on Python 3
        quantity = self.quantity if self.quantity else 0
        price_unit = self.price_unit if self.price_unit else 0
        return price_unit * quantity
    def __unicode__(self):  # __str__ on Python 3
        return '%s, %s'%(self.product.default_code,self.serial_number)


# INVOICE_STATES = (
#     ('draft', 'draft'),
#     ('proforma', 'proforma'),
#     ('proforma2', 'proforma2'),
#     ('open', 'open'),
#     ('paid', 'paid'),
#     ('cancel', 'cancel'),
# )
#
# class Invoice(models.Model):
#     # account_invoice
#     crm = models.ForeignKey('CRM')
#     payment_term = models.CharField(max_length=200) #payment_term_id in ERP
#     state = models.CharField(max_length=200, choices = INVOICE_STATES)
#     date_invoice = models.DateTimeField()
#     invoice_lines = models.ManyToManyField('Product', through='InvoiceLine')
#     #journal and account will be set in ERP - no need to reinvent the accounting wheel on frontend
#     #journal_id
#     #account_id
#
# #This should probably be a many to many field with Product and Invoice
# class InvoiceLine(models.Model):
#     # account_invoice_line
#     product = models.ForeignKey('Product', on_delete=models.CASCADE) #corresponds to product_product
#     invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
#     #account_id - income or expense account
#     quantity = models.FloatField()
#     #price = models.FloatField()
#     #tax set in ERP
#     #amount - calculated from quantity, price and tax - in ERP
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

