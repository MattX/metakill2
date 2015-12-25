from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm, PasswordInput, modelformset_factory
from django.contrib import messages

from . import models, forms, misc

# Create your views here.


def login(request):
    class LoginForm(ModelForm):
        class Meta:
            model = User
            fields = ['username', 'password']
            widgets = {
                'password': PasswordInput(),
            }

        def is_valid(self):
            return True

    login_form = LoginForm()

    if request.method == 'POST':
        u = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if u:
            auth_login(request, u)
            return redirect(list_killers)
        else:
            messages.add_message(request, messages.ERROR, "Mot de passe ou nom d'utilisateur incorrect")

    return render(request, 'login.html', {'login_form': login_form})


def new_killer(request):
    pass


def view_killer(request, id):
    killer = get_object_or_404(models.Killer, id=id)
    admin = False

    # General form
    kf = forms.KillerForm(instance=killer, prefix="general")

    if not request.user in list(killer.admins.all()) + list(killer.participants.all()):
        raise PermissionDenied

    if not request.user in killer.admins.all():
        misc.make_readonly(kf)
    else:
        admin = True
        if request.method == 'POST':
            kf = forms.KillerForm(request.POST, instance=killer, prefix="general")
            if kf.is_valid():
                kf.save()

    # Kills forms
    my_kills = models.Kill.objects.filter(writer=request.user).all()
    my_kill_forms = modelformset_factory(models.Kill, form=forms.KillFillForm, extra=0)\
        (queryset=my_kills, prefix="my_kills")

    # Kills table
    kills = {}

    for writer in killer.participants.all():
        kills[writer.pk] = {}
        for target in killer.participants.all():
            if writer == target:
                continue
            else:
                kills[writer.pk][target.pk] = models.Kill.objects.filter(killer=killer, writer=writer, target=target)\
                    .first()

    return render(request, 'view_killer.html', {'killer_form': kf, 'my_kill_forms': my_kill_forms, 'admin': admin})


def list_killers(request):
    my_killers = models.Killer.objects.filter(Q(participants__in=[request.user])|Q(admins__in=[request.user]))

    return render(request, 'list.html', {'killers': my_killers})
