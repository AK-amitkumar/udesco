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
        exclude = ['erpid']


# Create the form class.
class CRMForm(ModelForm):
    def __init__(self, *args, **kwargs):
        #self.instance = kwargs.pop('instance', None)


        # SET 'form-control' class on text fields to make them bootstrap style
        super(CRMForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text','email']:
                field.field.widget.attrs['class'] = 'form-control'
        #self.fields['customer'].required = False
        #self.fields['shop'].required = False

        # if self.instance.pk:
        #     self.initial['customer'] = self.instance.customer
        #     self.initial['shop'] = self.instance.shop
        #     self.initial['erpid'] = self.instance.erpid
        #     self.initial['state'] = self.instance.state


    class Meta:
        model = CRM
        exclude = ['crm_products','state','erpid','subs_erpid'] #'shop','customer'


'''
I need a CustomChoiceField that accepts .choices (CharField won't take .choices)
But I don't need the Choices validated method, which checks to see if the value selected
is in choices. When I set the units Select input in javascript, it doesn't update the
django choices, and the POST will fail validation.
Override validate https://github.com/django/django/blob/master/django/forms/fields.py
'''
class CustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class CRMProductFormsetLine(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CRMProductFormsetLine, self).__init__(*args, **kwargs)
        # choices = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
        # self.fields['product'].choices = choices
    #product = CustomChoiceField(widget=forms.TextInput(attrs={'class': 'product form-control'}))
    product_display = forms.CharField(
        required=False,
        # queryset = Food.objects.order_by('name'),
        # widget=forms.CheckboxSelectMultiple
        widget=forms.TextInput(attrs={'class': 'product_display'})
    )
    crm_product_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'crm_product_id'}), required=False)
    product_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'product_id'}), required=False)


    qty = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'qty form-control'}), required=False)
    serial_number = forms.CharField(widget=forms.TextInput(attrs={'class':'serial_number form-control'}), required=False)
    #make following readonly
    amount = forms.FloatField(widget=forms.NumberInput(attrs={'class':'amount form-control'}), required=False)
    #instead of passing initial to formset, I have to go one by one in form and pass as kwargs to forms in formset




class CRMProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # SET 'form-control' class on text fields to make them bootstrap style
        super(CRMProductForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text', 'email']:
                field.field.widget.attrs['class'] = 'form-control'
        # SET required = False to overwrite the form-control, which sets it to True
        self.fields['imei'].required = False
        self.fields['qty'].required = False

    class Meta:
        model = CRMProduct
        exclude = ['enable_state', 'condition','crm']