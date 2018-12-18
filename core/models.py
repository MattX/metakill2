from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from .misc import choose_and_remove

# Create your models here.

class Killer(models.Model):
    class Phases:
        initial = 0
        filling = 10
        playing = 20
        done = 30
    PHASE_CHOICES = [
        (Phases.initial, 'Sélection des participants'),
        (Phases.filling, 'Remplissage des kills'),
        (Phases.playing, 'Jeu en cours'),
        (Phases.done, 'Terminé'),
    ]

    participants = models.ManyToManyField(User, related_name='participating', blank=True)
    admins = models.ManyToManyField(User, related_name='administrating')

    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    phase = models.IntegerField(choices=PHASE_CHOICES, default=0)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return "Killer: " + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Guarantee that all kills exist
        for writer in self.participants.all():
            for target in self.participants.all():
                if writer == target:
                    continue
                elif not self.kill_set.filter(writer=writer, target=target).exists():
                    Kill(killer=self, writer=writer, target=target).save()

    def assign(self):
        if self.phase != Killer.Phases.filling:
            raise RuntimeError("Phase incorrecte pour assignation")

        for target in self.participants.all():
            suitable_kills = list(self.kill_set.filter(target=target))
            for assignee in self.participants.exclude(pk=target.pk):
                k = choose_and_remove(suitable_kills)
                k.assigned_to = assignee
                k.save()

        self.phase = Killer.Phases.playing
        self.save()

    def count_valid_kills(self):
        valid = []

        good_kills = self.kill_set.exclude(Q(desc__isnull=True)|Q(desc__exact=""))
        for u in self.participants.all():
            valid.append((u, good_kills.filter(writer=u).count()))

        return valid


class Kill(models.Model):
    killer = models.ForeignKey(Killer, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name='written', on_delete=models.PROTECT)
    target = models.ForeignKey(User, related_name='targetting', on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name='assigned', on_delete=models.PROTECT)
    desc = models.TextField(blank=True, null=True)
    done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('writer', 'target')

    def __str__(self):
        return "Kill de " + str(self.writer) + " pour " + str(self.target)
