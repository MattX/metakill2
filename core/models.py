from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Killer(models.Model):
    PHASES = [
        (0, 'Sélection des participants'),
        (10, 'Remplissage des kills'),
        (20, 'Jeu en cours'),
        (30, 'Terminé'),
    ]

    participants = models.ManyToManyField(User, related_name='participating', blank=True, null=True)
    admins = models.ManyToManyField(User, related_name='administrating')

    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    phase = models.IntegerField(choices=PHASES, default=0)

    def __str__(self):
        return "Killer: " + self.name

    # Guarantee that all kills exist
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for writer in self.participants.all():
            for target in self.participants.all():
                if writer == target:
                    continue
                elif not self.kill_set.filter(writer=writer, target=target).exists():
                    Kill(killer=self, writer=writer, target=target).save()


class Kill(models.Model):
    killer = models.ForeignKey(Killer)
    writer = models.ForeignKey(User, related_name='written')
    target = models.ForeignKey(User, related_name='targetting')
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name='assigned')
    desc = models.TextField(blank=True, null=True)
    done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('writer', 'target')

