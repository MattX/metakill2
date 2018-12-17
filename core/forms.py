from django import forms
from django.contrib.auth.models import User
from django_select2.forms import Select2MultipleWidget
from django.forms import PasswordInput

from . import models


class KillerForm(forms.ModelForm):
    class Meta:
        model = models.Killer
        fields = ['name', 'phase', 'participants', 'admins']
        widgets = {'participants': Select2MultipleWidget, 'admins': Select2MultipleWidget}


class KillFillForm(forms.ModelForm):
    class Meta:
        model = models.Kill
        fields = ['desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['desc'].label = self.instance.target


class KillDoneForm(forms.ModelForm):
    class Meta:
        model = models.Kill
        fields = ['done']


class AssignForm(forms.Form):
    assign_kills = forms.BooleanField(initial=False, required=False, help_text="Assigner les kills")


class PasswordForm(forms.Form):
    new_password = forms.CharField(widget=PasswordInput())
    confirm_password = forms.CharField(widget=PasswordInput())
