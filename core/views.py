from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ValidationError
from django.forms import ModelForm, PasswordInput, modelformset_factory
from django.contrib import messages
from django.contrib.auth.models import User
from metakill2.settings import CREATE_USER_SECRET

from . import models, forms, misc


# Create your views here.


def login_view(request):
    class LoginForm(ModelForm):
        class Meta:
            model = User
            fields = ['username', 'password']
            widgets = {'password': PasswordInput()}
            help_texts = {'username': ''}

        def is_valid(self):
            return True

    login_form = LoginForm()

    if request.method == 'POST':
        u = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if u:
            login(request, u)
            return redirect(list_killers)
        else:
            messages.add_message(request, messages.ERROR, "Mot de passe ou nom d'utilisateur incorrect")

    return render(request, 'login.html', {'login_form': login_form})


def view_killer(request, id):
    killer = get_object_or_404(models.Killer, id=id)
    admin = request.user in killer.admins.all()

    if not request.user.is_superuser and (request.user not in
                                          list(killer.admins.all()) + list(killer.participants.all())):
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

            if killer.phase == models.Killer.Phases.filling:
                af = forms.AssignForm(request.POST, prefix=assign_form_prefix)
                if af.is_valid() and af.cleaned_data['assign_kills']:
                    killer.assign()

        if killer.phase == models.Killer.Phases.filling:
            af = forms.AssignForm(prefix=assign_form_prefix)

    # Kills forms
    my_kill_forms_factory = modelformset_factory(models.Kill, form=forms.KillFillForm, extra=0)
    my_kills = killer.kill_set.filter(writer=request.user)

    my_kill_forms = my_kill_forms_factory(queryset=my_kills, prefix="my_kills")

    if request.method == 'POST' and killer.phase == models.Killer.Phases.filling:
        my_kill_forms = my_kill_forms_factory(request.POST, queryset=my_kills, prefix="my_kills")
        try:
            if my_kill_forms.is_valid():
                my_kill_forms.save()
        except ValidationError as e:
            messages.error(request, f"Erreur de validation: {e}")

    valid_count = killer.count_valid_kills()

    # Kills done table
    killer_kills = models.Kill.objects.filter(killer=killer)

    participants = list(killer.participants.all())
    kill_done_list = []

    for assigned_to in participants:
        assignee_kills = [assigned_to]
        for target in participants:
            if assigned_to == target:
                assignee_kills.append("")
            else:
                current_kill = killer_kills.filter(assigned_to=assigned_to, target=target).first()
                if current_kill is not None:
                    if admin and request.method == "POST":
                        current_kdf = forms.KillDoneForm(request.POST, instance=current_kill,
                                                         prefix="done_kills_" + str(current_kill.pk))
                        if current_kdf.is_valid():
                            current_kdf.save()

                    kdf = forms.KillDoneForm(instance=current_kill, prefix="done_kills_" + str(current_kill.pk))
                    if not admin:
                        misc.make_readonly(kdf)
                    assignee_kills.append(kdf)
                else:
                    assignee_kills.append(None)
        kill_done_list.append(assignee_kills)

    # Kills I must do
    my_assigned_kills = killer_kills.filter(assigned_to=request.user)

    # Scores
    class Score:
        def __init__(self, player, has_killed, was_killed):
            self.player = player
            self.has_killed = has_killed
            self.was_killed = was_killed
            self.total = has_killed * 1.5 - was_killed

    scores = []
    for p in killer.participants.all():
        scores.append(Score(p, killer.kill_set.filter(assigned_to=p, done=True).count(),
                            killer.kill_set.filter(target=p, done=True).count()))

    scores.sort(key=lambda score: score.total, reverse=True)

    # Completed kills
    kills_to_display = killer.kill_set.all()
    if killer.phase < killer.Phases.done:
        kills_to_display = kills_to_display.filter(done=True)

    return render(request, 'view_killer.html', {'killer_form': kf, 'my_kill_forms': my_kill_forms, 'admin': admin,
                                                'killer': killer, 'kill_done_dic': kill_done_list, 'assign_form': af,
                                                'participants': participants, 'my_assigned_kills': my_assigned_kills,
                                                'scores': scores, 'valid_count': valid_count,
                                                'kills_to_display': kills_to_display,
                                                'show_fill': killer.phase == killer.Phases.filling,
                                                'show_table': killer.phase >= killer.Phases.playing})


def list_killers(request):
    if request.user.is_superuser:
        my_killers = models.Killer.objects.all()
    else:
        my_killers = models.Killer.objects.filter(
            Q(participants__in=[request.user]) | Q(admins__in=[request.user])).distinct()

    return render(request, 'list.html', {'killers': my_killers})


def password_change(request):
    if request.method == 'POST':
        pf = forms.PasswordForm(request.POST)
        if pf.is_valid():

            if pf.cleaned_data['confirm_password'] != pf.cleaned_data['new_password']:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                new_pf = forms.PasswordForm()
                return render(request, 'password.html', {'password_form': new_pf})

            request.user.set_password(pf.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, "Mot de passe changé. Tu dois te reconnecter.")
            return redirect(list_killers)

    pf = forms.PasswordForm()
    return render(request, 'password.html', {'password_form': pf})


def logout_view(request):
    logout(request)
    messages.success(request, "Tu as été déconnecté.")
    return redirect(login_view)


def create_user_view(request):
    if request.user.is_authenticated:
        messages.error(request, "Tu ne peux pas créer un nouvel utilisateur en étant connecté.")
        return redirect(list_killers)

    if request.method == 'POST':
        cuf = forms.CreateUserForm(request.POST)
        if cuf.is_valid():

            if cuf.cleaned_data['secret_code'] != CREATE_USER_SECRET:
                messages.error(request, "Le code d'inscription est incorrect.")
                return render(request, 'create_user.html', {'create_user_form': cuf})

            u = User.objects.create_user(username=cuf.instance.username,
                    password=cuf.instance.password)

            default_killers = models.Killer.objects.filter(is_default=True).all()
            for k in default_killers:
                k.participants.add(u)
            login(request, u)
            messages.info(request, "Utilisateur créé.")

            return redirect(list_killers)

    cuf = forms.CreateUserForm()
    return render(request, 'create_user.html', {'create_user_form': cuf})

