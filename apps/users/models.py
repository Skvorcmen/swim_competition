from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        ORGANIZER = 'organizer', 'Организатор'
        COACH = 'coach', 'Тренер'


    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COACH,
    )