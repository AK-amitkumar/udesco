from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='smart_solar-home'),
    url(r'^(?P<crm_product_id>[0-9]+)/$', views.crm_product, name='crm_product'),
    url(r'^crm_product/datatable/$',views.CRMProductListJson.as_view(), name='crm_product_list_json'),
    #parameter is serial_number - filter to crm_product records for that unit
    #url(r'^crm_product/datatable/serial_number/(?P<serial_number>\w+)/$',views.CRMProductListJson.as_view(), name='crm_product_list_json'),
    url(r'^crm_product/datatable/(?P<cp>\w+)/(?P<crm_product_id>[0-9]+)/$',views.CRMProductListJson.as_view(), name='crm_product_list_json'),
    url(r'^crm_product/(?P<crm_product_id>[0-9]+)/$', views.crm_product, name='crm_product_detail'),
    url(r'^crm_product/$', views.crm_product, name='crm_product_detail'),
]