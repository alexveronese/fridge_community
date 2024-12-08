from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *

class CreateFridgeForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "fridge_crispy_form"
    helper.form_method = "POST"
    serial_number = forms.CharField(label="Serial Number", widget=forms.Textarea, max_length=10)
    secret_number = forms.CharField(label="Secret Number", widget=forms.Textarea, max_length=3)
    helper.add_input(Submit("Submit", "Confirm registration"))

    class Meta:
        model = Fridge
        fields = ["serial_number", "secret_number"]