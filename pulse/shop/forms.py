#https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#modelform

from django.forms import ModelForm
from .models import *

from django import forms



# Create the form class.
class CustomerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # SET 'form-control' class on text fields to make them bootstrap style
        super(CustomerForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text','email']:
                field.field.widget.attrs['class'] = 'form-control'
        # SET required = False to overwrite the form-control, which sets it to True
    class Meta:
        model = Customer
        exclude = []


# Create the form class.
class CRMForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # SET 'form-control' class on text fields to make them bootstrap style
        super(CRMForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text','email']:
                field.field.widget.attrs['class'] = 'form-control'
        # SET required = False to overwrite the form-control, which sets it to True
        #self.fields['street2'].required = False
    class Meta:
        model = CRM
        exclude = ['crm_products','state', 'customer']
    # name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # street2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # zip = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # #country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class CRMProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # SET 'form-control' class on text fields to make them bootstrap style
        super(CRMProductForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text', 'email']:
                field.field.widget.attrs['class'] = 'form-control'
        # SET required = False to overwrite the form-control, which sets it to True
        self.fields['imei'].required = False
        self.fields['quantity'].required = False

    class Meta:
        model = CRMProduct
        exclude = ['enable_state', 'condition','crm']