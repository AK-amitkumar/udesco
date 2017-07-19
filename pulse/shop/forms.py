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
        # SET 'form-control' class on text fields to make them bootstrap style
        super(CRMForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.field.widget.input_type in ['text','email']:
                field.field.widget.attrs['class'] = 'form-control'
        # SET required = False to overwrite the form-control, which sets it to True
        #self.fields['street2'].required = False
    class Meta:
        model = CRM
        exclude = ['crm_products','state', 'customer','erpid','shop']
    # name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # street2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # zip = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # #country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


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

    product_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'product_id'}), required=False)


    qty = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'qty form-control'}))
    serial_number = forms.CharField(widget=forms.TextInput(attrs={'class':'serial_number form-control'}))
    #make following readonly
    amount = forms.FloatField(widget=forms.NumberInput(attrs={'class':'amount form-control'}))
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