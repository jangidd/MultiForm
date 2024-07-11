from django.db import models

class Callback(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    qualification = models.CharField(max_length=100, null=True, default=None, blank=True)
    experience = models.PositiveIntegerField(null=True, default=None, blank=True)
    ctcheckbox = models.BooleanField(default=False)
    mricheckbox = models.BooleanField(default=False)
    xraycheckbox = models.BooleanField(default=False)
    mammographycheckbox = models.BooleanField(default=False)

    def __str__(self):
        return self.name
