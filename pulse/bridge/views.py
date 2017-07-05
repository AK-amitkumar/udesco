# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from . import demo

'''
   _____ __________.___                     .___             .__        __
  /  _  \\______   \   |   ____   ____    __| _/_____   ____ |__| _____/  |_  ______
 /  /_\  \|     ___/   | _/ __ \ /    \  / __ |\____ \ /  _ \|  |/    \   __\/  ___/
/    |    \    |   |   | \  ___/|   |  \/ /_/ ||  |_> >  <_> )  |   |  \  |  \___ \
\____|__  /____|   |___|  \___  >___|  /\____ ||   __/ \____/|__|___|  /__| /____  >
        \/                    \/     \/      \/|__|                  \/          \/
API 'endpoints' to call API functions below
'''


def make_demo(request):
    ret = demo.make_demo_function()
    return HttpResponse(ret)

def get_product_definitions(request):
    ret = demo.get_product_definitions_function()
    return HttpResponse(ret)

