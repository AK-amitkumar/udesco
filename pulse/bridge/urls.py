from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^make_demo$', views.make_demo, name='bridge_make_demo'),
    url(r'^get_product_definitions', views.get_product_definitions, name='bridge_get_product_definitions'),

]