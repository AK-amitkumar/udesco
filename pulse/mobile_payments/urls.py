from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'^$', views.index, name='mm-home'),
    url(r'^(?P<payment_id>[0-9]+)/$', views.payment, name='payment-detail'),
    url(r'^payment/datatable/$',views.PaymentListJson.as_view(), name='payment_list_json'),
    #for the following add a parameter shop_id
    url(r'^payment/datatable/(?P<shop_id>[0-9]+)/$',views.PaymentListJson.as_view(), name='payment_shop_list_json'),
    #mobile money provider screen in admin - no need to build a view
    #following is for the post from mobile money provider
    url(r'^payment_post', views.payment_post, name='payment_post'),
 ]