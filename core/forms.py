from django import forms
from django_select2.forms import Select2MultipleWidget

from . import models


class KillerForm(forms.ModelForm):
    class Meta:
        model = models.Killer
        fields = ['name', 'desc', 'phase', 'participants', 'admins']


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

