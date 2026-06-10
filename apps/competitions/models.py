from django.db import models
from apps.core.models import TimeStampModel


class Competition(TimeStampModel):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        REGISTRATION = 'registration', 'Приём заявок'
        CLOSED = 'closed', 'Заявки закрыты'
        IN_PROGRESS = 'in_progress', 'Идут заплывы'
        FINISHED = 'finished', 'Завершено'

    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    lanes_count = models.IntegerField(default=6)
    regulations_pdf = models.FileField(upload_to='regulations/', blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'
        ordering = ['-date']

    def __str__(self):
        return f'{self.name} {self.date}'

    def is_registration_open(self):
        from django.utils import timezone
        if self.status != self.Status.REGISTRATION:
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        return True


class Event(TimeStampModel):

    class Gender(models.TextChoices):
        MALE = 'male', 'Мужской'
        FEMALE = 'female', 'Женский'

    class Stroke(models.TextChoices):
        FREESTYLE = 'freestyle', 'Кроль на груди'
        BACKSTROKE = 'backstroke', 'На спине'
        BREASTSTROKE = 'breaststroke', 'Брасс'
        BUTTERFLY = 'butterfly', 'Баттерфляй'
        MEDLEY = 'medley', 'Комплекс'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        SEEDED = 'seeded', 'Заплывы сформированы'
        IN_PROGRESS = 'in_progress', 'Идут заплывы'
        FINISHED = 'finished', 'Завершено'

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    birth_year_from = models.IntegerField()
    birth_year_to = models.IntegerField()
    distance = models.IntegerField()
    stroke = models.CharField(max_length=20, choices=Stroke.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order']

    def __str__(self):
        return f'{self.get_gender_display()} {self.birth_year_from}-{self.birth_year_to} {self.distance}м {self.get_stroke_display()}'


class Application(TimeStampModel):

    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Подана'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    coach = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    excel_file = models.FileField(upload_to='applications/', blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка {self.coach} на {self.competition}'


class AthleteEvent(TimeStampModel):

    class ParticipationStatus(models.TextChoices):
        ACTIVE = 'active', 'Участвует'
        WITHDRAWN = 'withdrawn', 'Снялся'

    athlete = models.ForeignKey('teams.Athlete', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    preliminary_time = models.DurationField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_manually_added = models.BooleanField(default=False)
    participation_status = models.CharField(
        max_length=20,
        choices=ParticipationStatus.choices,
        default=ParticipationStatus.ACTIVE,
    )
    start_number = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Заявка спортсмена'
        verbose_name_plural = 'Заявки спортсменов'
        unique_together = ['athlete', 'event']

    def __str__(self):
        return f'{self.athlete} — {self.event}'


class Heat(TimeStampModel):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        IN_PROGRESS = 'in_progress', 'Идёт'
        FINISHED = 'finished', 'Завершён'

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    number = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = 'Заплыв'
        verbose_name_plural = 'Заплывы'
        ordering = ['number']

    def __str__(self):
        return f'Заплыв {self.number} — {self.event}'


class HeatLane(TimeStampModel):
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
    athlete_event = models.ForeignKey(AthleteEvent, on_delete=models.CASCADE)
    lane = models.IntegerField()
    result_time = models.DurationField(null=True, blank=True)
    dns = models.BooleanField(default=False)
    dnf = models.BooleanField(default=False)
    dsq = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'
        unique_together = ['heat', 'lane']

    def __str__(self):
        return f'Дорожка {self.lane} — {self.heat}'