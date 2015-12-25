from django.contrib import admin
from . import models

# Register your models here.

r = admin.site.register

r(models.Killer)
r(models.Kill)

