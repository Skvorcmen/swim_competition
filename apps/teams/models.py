from django.db import models
from apps.core.models import TimeStampModel
from apps.users.models import User


class Team(TimeStampModel):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    coach = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams'
    )

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return f'{self.name} — {self.city}'


class Athlete(TimeStampModel):

    class Gender(models.TextChoices):
        MALE = 'male', 'Мужской'
        FEMALE = 'female', 'Женский'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_year = models.IntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='athletes'
    )
    coach = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='athletes'
    )
    application = models.ForeignKey(
        'competitions.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='athletes'
    )

    class Meta:
        verbose_name = 'Спортсмен'
        verbose_name_plural = 'Спортсмены'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.birth_year}'