from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from boiler_plate.helper import unique_slug_generator


class User(AbstractUser):
    GENDER_CHOICES = (
        ('1', 'Male'),
        ('2', 'Female'),
    )
    mobile = models.CharField(max_length=15, blank=True, null=True)
    gender = models.IntegerField(null=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    slug = models.CharField(max_length=500, default="")

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(name=self.username, class_name=User)
        super().save(*args, **kwargs)
