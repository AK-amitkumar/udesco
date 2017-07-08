from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views
from smart_solar import views as ss_views

urlpatterns = [
    url(r'^$', views.index, name='shop-home'),
    url(r'^(?P<shop_id>[0-9]+)/$', views.shop, name='shop-detail'),
    url(r'^shop/datatable/$',views.ShopListJson.as_view(), name='shop_list_json'),
    #for the following add a parameter shop_id
    url(r'^crm/datatable/(?P<shop_id>[0-9]+)/$',views.CRMListJson.as_view(), name='crm_list_json'),
    url(r'^customer/(?P<customer_id>[0-9]+)/$', views.customer, name='customer_detail'),
    url(r'^customer/$', views.customer, name='customer_detail'),
    url(r'^crm/(?P<crm_id>[0-9]+)/$', views.crm, name='crm_detail'),
    url(r'^crm/$', views.crm, name='crm_detail'),
    # parameter is crm_id - filter to crm_product records for that crm
    url(r'^crm_product/datatable/crm_id/(?P<crm_id>[0-9]+)/$', ss_views.CRMProductListJson.as_view(),
        name='crm_product_list_json'),
    #for the autocomplete field
    url(r'^product_select_options/$', views.product_select_options, name='product_select_options'),
    url(r'^qty_remaining/$', views.qty_remaining, name='qty_remaining'),
    
    ]