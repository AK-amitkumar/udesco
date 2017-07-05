
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

from faker import Faker
fake = Faker()

from random import randint
import datetime


'''
select * from res_country
select * from res_company --name, partner_id, email, phone
select crm from res_partner --name, company_id, country_id, email, phone, street, street2, city, zip, is_company, supplier (bool), crm (bool)
select * from res_users --login, password, company_id, partner_id, active
select * from product_product --default_code, product_template_id
select * from product_template --list_price, default_code, company_id

'''

def make_demo_function():
    print 'MAKING FAKE ORGANIZATION w ERP and FAKE DATA'
    print 'countries from ERP res_country table'
    get_countries()
    print 'companies from ERP res_company table - shops withing that company with FAKE data'
    get_company_and_make_shop_and_crms()
    print 'get physical products from ERP product_template table'
    get_product_definitions_function()
    print 'Creating CRMProducts - there should be some kind of create override that creates draft account_invoice in ERP'
    make_crm_products()
    return True



def get_countries():
    #get countries from res_country table
    vals = api.search_read_erp('res.country', [], ['name','code'])
    for v in vals:
        #print v
        p, c = Country.objects.get_or_create(code=v['code'], name=v['name'])


def get_company_and_make_shop_and_crms():
    #get company from res_company table

    #link Pulse company to Pulse country depending on what link is in ERP
    vals = api.search_read_erp('res.partner', [], ['name', 'company_id', 'country_id', 'email', 'phone',
                                               'street', 'street2', 'city', 'zip', 'is_company',
                                               'supplier', 'crm' ])
    for v in vals:
        if v.get('is_company'):
            #print v
            try:
                country=None
                if v.get('country_id'):
                    country_name =  v.get('country_id')[1]
                    res = Country.objects.filter(name=country_name)#__icontains=str(country_name))
                    if len(res)>0:
                        country = res[0]
                    else:
                        country = Country.objects.get(id=5)
                comp, c = Company.objects.get_or_create(name=v['name'], country=country)
                print 'comp-country',country, comp.country
                # email=v['email'], phone = v['phone'],
                # street=v['street'],street2=v['street2'],
                # zip=v['zip'],city=v['city'],
                if comp:
                    for i in range(3):
                        s, c = Shop.objects.get_or_create(name=fake.company(), company = comp, country=country,
                        email=fake.email(), phone = fake.phone_number(),
                        street=fake.street_address(),#street2=fake.email(),
                        zip=fake.zipcode(),city=fake.city())
                        print 'shop-country', country, comp.country
                        print 'MAKING CRM and CUSTOMERS FOR SHOP %s'%s.name
                        make_crms(comp,country,s)
            except Exception as e:
                print e


def make_crms(comp,country,shop):
    for j in range(50):
        try:
            cust, cr = Customer.objects.get_or_create(uid=fake.ssn(),first=fake.first_name(),last=fake.last_name(),#company = comp,
                            email=fake.email(), phone = fake.phone_number(),country=country,
                            street=fake.street_address(),#street2=fake.email(),
                            zip=fake.zipcode(),city=fake.city())
            CRM.objects.get_or_create(uid=cust.uid,customer=cust,shop=shop)
        except Exception as e:
            print e #faker not generating unique ppl
    return None



def get_product_definitions_function():
    # get some product definitions from ERP
    #type = consu, service, product (Consumable aka don't manage Inventory, Service non-physical, Stockable Product aka manage stock
    vals = api.search_read_erp('product.template', [('type','in',['consu','product'])], ['name', 'default_code', 'list_price' ])
    for v in vals:
        #print v
        prod, c = Product.objects.get_or_create(name=v['name'], default_code=v['default_code'],list_price=v['list_price'])
    return None


def make_crm_products():
    crms = CRM.objects.all()
    products = Product.objects.all()
    print 'Creating CRMProducts - there should be some kind of create override that creates draft account_invoice in ERP'
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
