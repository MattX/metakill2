from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm, PasswordInput, modelformset_factory, modelform_factory
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
    admin = request.user in killer.admins.all()


    if not request.user in list(killer.admins.all()) + list(killer.participants.all()):
        raise PermissionDenied


    # General form
    general_form_prefix = "general"
    assign_form_prefix = "assign"
    kf = forms.KillerForm(instance=killer, prefix=general_form_prefix)
    af = None

    if not admin:
        misc.make_readonly(kf)
    else:
        if request.method == 'POST':
            kf = forms.KillerForm(request.POST, instance=killer, prefix=general_form_prefix)
            if kf.is_valid():
                kf.save()

            af = forms.AssignForm(request.POST, prefix=assign_form_prefix)
            print(af.is_valid())
            if af.cleaned_data['assign_kills']:
                killer.assign()
        af = forms.AssignForm(prefix=assign_form_prefix)


    # Kills forms
    kills_forms_prefix = "my_kills"
    my_kill_forms_factory = modelformset_factory(models.Kill, form=forms.KillFillForm, extra=0)
    my_kills = models.Kill.objects.filter(writer=request.user)

    my_kill_forms = my_kill_forms_factory(queryset=my_kills, prefix="my_kills")

    if request.method == 'POST' and killer.phase == models.Killer.Phases.filling:
        my_kill_forms = my_kill_forms_factory(request.POST, queryset=my_kills, prefix="my_kills")
        if my_kill_forms.is_valid():
            my_kill_forms.save()

    # Kills done table
    killer_kills = models.Kill.objects.filter(killer=killer)

    participants = list(killer.participants.all())
    kill_done_list = []

    for assigned_to in participants:
        assignee_kills = []
        for target in participants:
            if assigned_to == target:
                assignee_kills.append("X")
            else:
                current_kill = killer_kills.filter(assigned_to=assigned_to, target=target).first()
                if not current_kill is None:
                    if admin and request.method == "POST":
                        current_kdf = forms.KillDoneForm(request.POST, instance=current_kill,
                                                         prefix="done_kills_" + str(current_kill.pk))
                        if current_kdf.is_valid():
                            current_kdf.save()
                    assignee_kills.append(forms.KillDoneForm(instance=current_kill,
                                                             prefix="done_kills_" + str(current_kill.pk)))
                else:
                    assignee_kills.append(None)
        kill_done_list.append(assignee_kills)

    return render(request, 'view_killer.html', {'killer_form': kf, 'my_kill_forms': my_kill_forms, 'admin': admin,
                                                'killer': killer, 'kill_done_dic': kill_done_list, 'assign_form': af,
                                                'participants': participants,
                                                'show_fill': killer.phase == killer.Phases.filling,
                                                'show_table': killer.phase >= killer.Phases.playing})


def list_killers(request):
    my_killers = models.Killer.objects.filter(Q(participants__in=[request.user]) | Q(admins__in=[request.user])).distinct()

    return render(request, 'list.html', {'killers': my_killers})
