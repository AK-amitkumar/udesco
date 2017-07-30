
'''
________                          ___________                   __  .__
\______ \   ____   _____   ____   \_   _____/_ __  ____   _____/  |_|__| ____   ____   ______
 |    |  \_/ __ \ /     \ /  _ \   |    __)|  |  \/    \_/ ___\   __\  |/  _ \ /    \ /  ___/
 |    `   \  ___/|  Y Y  (  <_> )  |     \ |  |  /   |  \  \___|  | |  (  <_> )   |  \\___ \
/_______  /\___  >__|_|  /\____/   \___  / |____/|___|  /\___  >__| |__|\____/|___|  /____  >
        \/     \/      \/              \/             \/     \/                    \/     \/
Use API Functions Below to create demo data for Pulse (fake and from ERP)

'''


from smart_solar.models import *
from shop.models import *
from mobile_payments.models import *

from faker import Faker
fake = Faker()

from random import randint
import datetime


#following is NOT postgres database settings - it is odoo settings
#pg database connections are supposed to match with odoo10/debian/odoo.conf

import api

UID = api.auth_erp()



def make_demo_function():
    get_newly_generated_draft_invoices()
    # print 'ERP res_country --> Django Country'
    # get_countries()
    # print 'ERP res_partner --> Django Company (erpid of res_partner id)'
    # comp_list = get_companies()
    # print 'DJANGO Shop'
    # for comp in comp_list:
    #     make_shops(comp)
    # print 'SANITY CHECK'
    # get_customers()
    # print 'ERP product_template --> Django Product (erpid of product_template id)'
    # get_products()
    # print 'Django CRMProduct --> ERP sales_order'
    # make_crm_products()
    # print 'Creating Django MM Provider'
    # make_mm_provider()
    # print 'Invoice all customers in third shop'
    # make_invoices()
    # return True


def make_shops(comp):
    for i in range(2):#2 shops per company
        shop, c = Shop.objects.get_or_create(name=fake.company(), company=comp, country=comp.country,
                                          email=fake.email(), phone=fake.phone_number(),
                                          street=fake.street_address(),  # street2=fake.email(),
                                          zip=fake.zipcode(), city=fake.city())
        print 'Django Customer --> ERP res_partner (customer = True)'
        print 'Django CRM --> ERP sales_order (draft) (erpid of sales_order id)'
        make_customers(shop)


def make_customers(shop):
    for j in range(50):
        try:
            erpid = fake.random_int()*fake.random_int()/fake.random_int()
            cust, cr = Customer.objects.get_or_create(erpid=erpid,name=fake.first_name()+' '+fake.last_name(),#company = comp,
                            email=fake.email(), phone = fake.phone_number(),country=shop.country,
                            street=fake.street_address(),#street2=fake.email(),
                            zip=fake.zipcode(),city=fake.city())
            CRM.objects.get_or_create(erpid=erpid,customer=cust,shop=shop)
        except Exception as e:
            print e
    return None



def make_crm_products():
    crms = CRM.objects.all()
    products = Product.objects.all()
    for i,c in enumerate(crms):
        rando =  randint(0,5)
        if rando == 1:
            p,cr = CRMProduct.objects.get_or_create(crm=c,product=products[0],serial_number='SN%s%s%s'%(fake.uuid4(),1,i))
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[1],serial_number='SN%s%s%s'%(fake.uuid4(),2,i))
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[2],serial_number='SN%s%s%s'%(fake.uuid4(),3,i))
        elif rando == 2:
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[0],serial_number='SN%s%s%s'%(fake.uuid4(),4,i))
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[1],serial_number='SN%s%s%s'%(fake.uuid4(),5,i))
        elif rando == 3:
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[0],serial_number='SN%s%s%s'%(fake.uuid4(),6,i))
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[2],serial_number='SN%s%s%s'%(fake.uuid4(),7,i))
        elif rando == 4:
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[1],serial_number='SN%s%s%s'%(fake.uuid4(),8,i))
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[2],serial_number='SN%s%s%s'%(fake.uuid4(),9,i))
        elif rando == 5:
            p, cr = CRMProduct.objects.get_or_create(crm=c, product=products[1],serial_number='SN%s%s%s'%(fake.uuid4(),10,i))

def make_mm_provider():
    MMProvider.objects.get_or_create(name='KopoKopo',username='bboxx',
                                     password='d0Mi7ANGCv6D',
                                     key='5aaa3b74cbe45ddcbfe5badec141b380bf63a444')


#make invoices - by calling
def make_invoices():
    crms = CRM.objects.filter(shop=3, state='draft') # make all of the crms in the third shop invoiced
    for crm in crms:
        customer = crm.customer
        customer.phone = "+254716050%s"%crm.id   #"+254716050964"
        customer.save()
        if len(crm.crm_products.all()) > 0:
            crm.action_invoice_create_and_open()
            #crm.action_invoice_open()




''' 
 ____ ___            .___       __           ___________                   __  .__                      
|    |   \______   __| _/____ _/  |_  ____   \_   _____/_ __  ____   _____/  |_|__| ____   ____   ______
|    |   /\____ \ / __ |\__  \\   __\/ __ \   |    __)|  |  \/    \_/ ___\   __\  |/  _ \ /    \ /  ___/
|    |  / |  |_> > /_/ | / __ \|  | \  ___/   |     \ |  |  /   |  \  \___|  | |  (  <_> )   |  \\___ \ 
|______/  |   __/\____ |(____  /__|  \___  >  \___  / |____/|___|  /\___  >__| |__|\____/|___|  /____  >
          |__|        \/     \/          \/       \/             \/     \/                    \/     \/ 

Following functions grab data generated in the ERP (usually through Cron Jobs)
'''


def get_pulse_country_id_from_erp_related_field(erp_vals):
    if not erp_vals['country_id']:
        return erp_vals
    else:
        new_erp_vals = erp_vals.copy()
        erpid = erp_vals['country_id'][0]
        qs = Country.objects.filter(erpid = erpid)
        if qs.exists():
            new_erp_vals['country_id'] = qs[0].id
        return new_erp_vals
            
            
            

def get_countries():
    # get countries from res_country table
    vals = api.search_read_erp('res.country', [], ['id', 'name', 'code'])
    for v in vals:
        # if a country is already created in pulse, then update it if ERP values have changed
        queryset = Country.objects.filter(erpid=v['id'])
        if queryset.exists():
            v.pop('id')
            for attr, value in v.iteritems():
                setattr(queryset[0], attr, value)
            queryset[0].save()


        # else get_or_create in pulse
        else:
            p, c = Country.objects.get_or_create(code=v['code'], name=v['name'])

def get_companies():
    comp_list = []
    # get company from res_partner table
    vals = api.search_read_erp('res.partner', [], ['id', 'name', 'company_id', 'country_id', 'email', 'phone',
                                               'street', 'street2', 'city', 'zip', 'is_company',
                                               'supplier', 'customer'])
    for ov in vals:
        # if a company is already created in pulse, then update it if ERP values have changed
        v = get_pulse_country_id_from_erp_related_field(ov)

        queryset = Company.objects.filter(erpid=v['id'])
        if queryset.exists():
            v.pop('id')
            for attr, value in v.iteritems():
                setattr(queryset[0], attr, value)
            queryset[0].save()

        # else get_or_create in pulse
        else:
            if v.get('is_company'):
                try:
                    comp, c = Company.objects.get_or_create(erpid=v['id'], name=v['name'], country_id=v['country_id'])
                    comp_list.append(comp)
                except Exception as e:
                    log.error(e)
            else:
                continue
    return comp_list
    #raise Exception('Could not get a company res_partner from odoo - make one first')

def get_products():
    # get some product definitions from product_template
    # type = consu, service, product (Consumable aka don't manage Inventory, Service non-physical, Stockable Product aka manage stock
    # If the product's invoice policy is deliver, then you cannot invoice the quotation (not until delivery) - for demo I want to invoice on order
    vals = api.search_read_erp('product.template',
                           [('invoice_policy', '=', 'order'), ('type', 'in', ['consu', 'product'])],
                           ['name', 'default_code', 'list_price', 'type'])
    for v in vals:

        # if a product is already created in pulse, then update it if ERP values have changed
        queryset = Product.objects.filter(template_erpid=v['id'])
        if queryset.exists():
            v.pop('id')
            for attr, value in v.iteritems():
                setattr(queryset[0], attr, value)
            queryset[0].save()

        # else get_or_create in pulse
        else:
            prod, c = Product.objects.get_or_create(name=v['name'],
                                                    default_code=v['default_code'],
                                                    list_price=v['list_price']
                                                    , type=v['type'])
    return True

def get_customers():
    # get some product definitions from product_template
    # type = consu, service, product (Consumable aka don't manage Inventory, Service non-physical, Stockable Product aka manage stock
    # If the product's invoice policy is deliver, then you cannot invoice the quotation (not until delivery) - for demo I want to invoice on order
    vals = api.search_read_erp('res.partner',
                           [('customer', '=', True)],
                           ['name', 'city', 'street', 'street2', 'zip', 'country_id', 'email', 'phone'])
    for ov in vals:
        # if a company is already created in pulse, then update it if ERP values have changed
        v = get_pulse_country_id_from_erp_related_field(ov)
        queryset = Customer.objects.filter(erpid=v['id'])
        if queryset.exists():
            v.pop('id')
            for attr, value in v.iteritems():
                setattr(queryset[0], attr, value)
            queryset[0].save()

        # else get_or_create in pulse
        else:
            cust, cr = Customer.objects.get_or_create(erpid=v['id'], name=v['name'],
                                                      email=v['email'], phone=v['phone'],
                                                      country_id=v['country_id'],
                                                      street=v['street'],
                                                      zip=v['zip'], city=v['city'])
    return True

def get_suppliers():
    # get some product definitions from product_template
    # type = consu, service, product (Consumable aka don't manage Inventory, Service non-physical, Stockable Product aka manage stock
    # If the product's invoice policy is deliver, then you cannot invoice the quotation (not until delivery) - for demo I want to invoice on order

    vals = api.search_read_erp('res.partner',
                               [('supplier', '=', True)],
                               ['name', 'city', 'street', 'street2', 'zip', 'country_id', 'email', 'phone'])
    for ov in vals:
        # if a company is already created in pulse, then update it if ERP values have changed
        v = get_pulse_country_id_from_erp_related_field(ov)
        # if a product is already created in pulse, then update it if ERP values have changed
        queryset = Supplier.objects.filter(erpid=v['id'])
        if queryset.exists():
            v.pop('id')
            for attr, value in v.iteritems():
                setattr(queryset[0], attr, value)
            queryset[0].save()

        # else get_or_create in pulse
        else:
            cust, cr = Supplier.objects.get_or_create(erpid=v['id'], name=v['name'],
                                                      email=v['email'], phone=v['phone'],
                                                      country_id=v['country_id'],
                                                      street=v['street'],
                                                      zip=v['zip'], city=v['city'])
    return True



def get_newly_generated_draft_invoices():  # 'action_invoice_create' in kwargs:
    log.info('Celery Scheduled Invoivce Check')

    read_dict_list = api.search_read_erp('account.invoice', [('state','=','draft')],['id','origin'])
    log.info('# of draft invoices = %s'%len(read_dict_list))
    for read_dict in read_dict_list:
        log.info(read_dict)
        sale_order_ids = api.search_erp('sale.order', [('name', '=', read_dict['origin'])])
        log.info('SO = %s'%read_dict['origin'])
        if sale_order_ids:
            crm = CRM.objects.get(erpid = sale_order_ids[0])
            # todo only create new draft invoice if customer has paid last invoice
            log.info('Creating Invoice')
            new_draft_invoice, cr = Invoice.objects.get_or_create(erpid=read_dict['id'], crm=crm)
            log.info('call action_invoice_open() on invoice %s'%new_draft_invoice.id)
            # todo OR MAYBE only post invoice if customer has paid last invoice
            #post invoice and apply payments
            new_draft_invoice.action_invoice_open()
    return True

                #dir(fake)

# ['_Generator__config', '_Generator__format_token', '__class__', '__delattr__', '__dict__',
#  '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__',
#  '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__'
#     , '__weakref__', 'add_provider', 'address', 'am_pm', 'binary', 'boolean', 'bothify', 'bs', 'building_number',
#  'catch_phrase', 'century', 'chrome', 'city', 'city_prefix', 'city_suffix', 'color_name', 'company', 'company_email'
#     , 'company_suffix', 'country', 'country_code', 'credit_card_expire', 'credit_card_full', 'credit_card_number',
#  'credit_card_provider', 'credit_card_security_code', 'currency_code', 'date', 'date_object', 'date_time', 'date_time_ad',
#  'date_time_between', 'date_time_between_dates', 'date_time_this_century', 'date_time_this_decade', 'date_time_this_month',
#  'date_time_this_year', 'day_of_month', 'day_of_week', 'domain_name', 'domain_word', 'ean', 'ean13', 'ean8', 'email',
#  'file_extension', 'file_name', 'file_path', 'firefox', 'first_name', 'first_name_female', 'first_name_male', 'format',
#  'free_email', 'free_email_domain', 'future_date', 'future_datetime', 'geo_coordinate', 'get_formatter', 'get_providers',
#  'hex_color', 'image_url', 'internet_explorer', 'ipv4', 'ipv6', 'isbn10', 'isbn13', 'iso8601', 'job', 'language_code',
#  'last_name', 'last_name_female', 'last_name_male', 'latitude', 'lexify', 'linux_platform_token', 'linux_processor',
#  'locale', 'longitude', 'mac_address', 'mac_platform_token', 'mac_processor', 'md5', 'military_apo', 'military_dpo',
#  'military_ship', 'military_state', 'mime_type', 'month', 'month_name', 'name', 'name_female', 'name_male', 'null_boolean',
#  'numerify', 'opera', 'paragraph', 'paragraphs', 'parse', 'password', 'past_date', 'past_datetime', 'phone_number',
#  'postalcode', 'postalcode_plus4', 'postcode', 'prefix', 'prefix_female', 'prefix_male', 'profile', 'provider',
#  'providers', 'pybool', 'pydecimal', 'pydict', 'pyfloat', 'pyint', 'pyiterable', 'pylist', 'pyset', 'pystr',
#  'pystruct', 'pytuple', 'random', 'random_digit', 'random_digit_not_null', 'random_digit_not_null_or_empty',
#  'random_digit_or_empty', 'random_element', 'random_int', 'random_letter', 'random_number', 'random_sample',
#  'random_sample_unique', 'randomize_nb_elements', 'rgb_color', 'rgb_color_list', 'rgb_css_color', 'safari', ''
# 'safe_color_name', 'safe_email', 'safe_hex_color', 'secondary_address', 'seed', 'sentence', 'sentences',
#  'set_formatter', 'sha1', 'sha256', 'simple_profile', 'slug', 'ssn', 'state', 'state_abbr', 'street_address',
#  'street_name', 'street_suffix', 'suffix', 'suffix_female', 'suffix_male', 'text', 'time', 'time_delta',
#  'time_object', 'timezone', 'tld', 'unix_time', 'uri', 'uri_extension', 'uri_page', 'uri_path', 'url',
#  'user_agent', 'user_name', 'uuid4', 'windows_platform_token', 'word', 'words', 'year', 'zipcode', 'zipcode_plus4']