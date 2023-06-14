from django.db import models


class Users(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField(default=18)
    address = models.CharField(max_length=200)

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'
