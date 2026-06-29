import random
from datetime import timedelta, datetime, date

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.competitions.models import Competition, Event, Application, AthleteEvent
from apps.teams.models import Team, Athlete
from apps.users.models import User


FIRST_NAMES_M = ['Иван', 'Петр', 'Семен', 'Кирилл', 'Максим', 'Влад', 'Захар', 'Олег', 'Андрей', 'Денис', 'Артем', 'Никита', 'Степан', 'Глеб']
FIRST_NAMES_F = ['Анна', 'Мария', 'Елена', 'Ольга', 'Дарья', 'София', 'Алина', 'Виктория', 'Полина', 'Ксения', 'Ирина', 'Юлия', 'Алиса', 'Вера']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Морозов', 'Волков', 'Зайцев', 'Орлов', 'Соколов', 'Лебедев', 'Новиков', 'Попов', 'Васильев', 'Смирнов', 'Кузнецов', 'Андреев', 'Беляев', 'Гусев']

TEAM_NAMES = ['Дельфин', 'Акула', 'Волна', 'Нептун', 'Чемпион', 'Старт']
CITIES = ['Астана', 'Алматы', 'Шымкент']


def random_time(distance, base_seconds_per_50m=28):
    """Генерирует случайное реалистичное время в зависимости от дистанции."""
    segments = distance // 50
    total_seconds = base_seconds_per_50m * segments + random.uniform(-3, 6) * segments
    total_seconds = max(total_seconds, 15)
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return timedelta(minutes=minutes, seconds=seconds)


class Command(BaseCommand):
    help = 'Генерирует тестовое соревнование с категориями, командами и спортсменами'

    def handle(self, *args, **options):
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('Не найден суперпользователь. Создайте через createsuperuser.'))
            return

        # 1. Создаём соревнование
        competition = Competition.objects.create(
            name='Большой кубок iSwim',
            date=date.today() + timedelta(days=14),
            location='Астана, бассейн Нурлы',
            lanes_count=8,
            status=Competition.Status.REGISTRATION,
            registration_deadline=timezone.now() + timedelta(days=7),
            is_open=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Создано соревнование: {competition} (id={competition.id})'))

        # 2. Создаём категории
        categories_data = [
            ('male', 2012, 2014, 50, 'freestyle', 1),
            ('female', 2012, 2014, 50, 'freestyle', 2),
            ('male', 2010, 2011, 100, 'breaststroke', 3),
            ('female', 2010, 2011, 100, 'breaststroke', 4),
            ('male', 2012, 2014, 50, 'backstroke', 5),
        ]

        events = []
        for gender, year_from, year_to, distance, stroke, order in categories_data:
            event = Event.objects.create(
                competition=competition,
                gender=gender,
                birth_year_from=year_from,
                birth_year_to=year_to,
                distance=distance,
                stroke=stroke,
                order=order,
            )
            events.append(event)
            self.stdout.write(f'  Категория: {event}')

        # 3. Создаём команды
        teams = []
        for name in TEAM_NAMES:
            team = Team.objects.create(
                name=name,
                city=random.choice(CITIES),
                coach=admin_user,
            )
            teams.append(team)

        self.stdout.write(self.style.SUCCESS(f'Создано команд: {len(teams)}'))

        # 4. Создаём заявку
        application = Application.objects.create(
            competition=competition,
            coach=admin_user,
            status=Application.Status.ACCEPTED,
        )

        # 5. Генерируем спортсменов на каждую категорию
        total_athletes = 0
        for event in events:
            athletes_count = random.randint(10, 16)

            for i in range(athletes_count):
                if event.gender == 'male':
                    first_name = random.choice(FIRST_NAMES_M)
                else:
                    first_name = random.choice(FIRST_NAMES_F)

                last_name = random.choice(LAST_NAMES)
                birth_year = random.randint(event.birth_year_from, event.birth_year_to)
                team = random.choice(teams)

                athlete = Athlete.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    birth_year=birth_year,
                    gender=event.gender,
                    team=team,
                    coach=admin_user,
                    application=application,
                )

                # 10% спортсменов без предварительного времени
                has_time = random.random() > 0.1
                preliminary_time = random_time(event.distance) if has_time else None

                AthleteEvent.objects.create(
                    athlete=athlete,
                    event=event,
                    application=application,
                    preliminary_time=preliminary_time,
                    is_paid=True,
                )

                total_athletes += 1

        self.stdout.write(self.style.SUCCESS(f'Создано спортсменов: {total_athletes}'))
        self.stdout.write(self.style.SUCCESS(f'\nГотово! ID соревнования: {competition.id}'))
        self.stdout.write(f'Открой: http://127.0.0.1:8000/competitions/{competition.id}/heats/ после формирования заплывов')