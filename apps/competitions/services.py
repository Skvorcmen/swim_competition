import random
from apps.competitions.models import Event, AthleteEvent, Heat, HeatLane


def get_snake_lane_order(lanes_count):
    """
    Возвращает порядок дорожек от центра к краям.
    Для 6 дорожек: [4, 3, 5, 2, 6, 1]
    Для 8 дорожек: [4, 5, 3, 6, 2, 7, 1, 8]
    """
    center = lanes_count // 2
    order = []
    left = center
    right = center + 1

    for i in range(lanes_count):
        if i % 2 == 0:
            order.append(right)
            right += 1
        else:
            order.append(left)
            left -= 1

    return order


def split_into_heats(athletes_count, lanes_count):
    """
    Делит количество спортсменов на заплывы.
    Минимум 3 человека в заплыве (кроме случаев когда всего меньше 3).
    Возвращает список размеров заплывов, например [4, 5, 5].
    """
    if athletes_count <= lanes_count:
        return [athletes_count]

    heats_count = -(-athletes_count // lanes_count)  # округление вверх

    base = athletes_count // heats_count
    remainder = athletes_count % heats_count

    heat_sizes = [base] * heats_count
    for i in range(remainder):
        heat_sizes[-(i + 1)] += 1

    return heat_sizes


def form_heats_for_event(event, starting_heat_number=1):
    competition = event.competition
    lanes_count = competition.lanes_count

    athlete_events = AthleteEvent.objects.filter(
        event=event,
        participation_status=AthleteEvent.ParticipationStatus.ACTIVE,
    )

    with_time = list(athlete_events.filter(preliminary_time__isnull=False))
    without_time = list(athlete_events.filter(preliminary_time__isnull=True))

    with_time.sort(key=lambda ae: ae.preliminary_time, reverse=True)
    random.shuffle(without_time)

    ordered_athletes = with_time + without_time

    total = len(ordered_athletes)
    if total == 0:
        return starting_heat_number

    heat_sizes = split_into_heats(total, lanes_count)
    lane_order = get_snake_lane_order(lanes_count)

    heat_number = starting_heat_number
    index = 0

    for size in heat_sizes:
        heat_athletes = ordered_athletes[index:index + size]
        index += size

        heat = Heat.objects.create(
            event=event,
            number=heat_number,
        )

        lanes_for_this_heat = lane_order[:size]
        reversed_lanes = list(reversed(lanes_for_this_heat))

        for athlete_event, lane in zip(heat_athletes, reversed_lanes):
            HeatLane.objects.create(
                heat=heat,
                athlete_event=athlete_event,
                lane=lane,
            )

        heat_number += 1

    event.status = Event.Status.SEEDED
    event.save()

    return heat_number


def calculate_results_for_event(event):
    """
    Подсчитывает места для всех спортсменов категории (Event)
    после того как все заплывы этой категории завершены.
    Возвращает список словарей, отсортированный: сначала места по времени,
    затем DNS/DNF/DSQ без места.
    """
    from apps.competitions.models import Heat, HeatLane

    heats = Heat.objects.filter(event=event)

    if heats.filter(status=Heat.Status.PENDING).exists():
        return None

    all_lanes = HeatLane.objects.filter(
        heat__event=event
    ).select_related('athlete_event__athlete', 'heat')

    finished_lanes = [l for l in all_lanes if l.result_time and not (l.dns or l.dnf or l.dsq)]
    non_finished_lanes = [l for l in all_lanes if l.dns or l.dnf or l.dsq]

    sorted_lanes = sorted(finished_lanes, key=lambda l: l.result_time)

    results = []
    current_place = 1

    for i, lane in enumerate(sorted_lanes):
        if i > 0 and lane.result_time == sorted_lanes[i - 1].result_time:
            place = results[-1]['place']
        else:
            place = current_place

        results.append({
            'place': place,
            'athlete': lane.athlete_event.athlete,
            'time': lane.result_time,
            'heat_number': lane.heat.number,
            'lane': lane.lane,
            'status': None,
        })

        current_place += 1

    # Добавляем DNS/DNF/DSQ без места, в конец протокола
    for lane in non_finished_lanes:
        if lane.dns:
            status = 'DNS'
        elif lane.dnf:
            status = 'DNF'
        elif lane.dsq:
            status = 'DSQ'
        else:
            status = None

        results.append({
            'place': None,
            'athlete': lane.athlete_event.athlete,
            'time': None,
            'heat_number': lane.heat.number,
            'lane': lane.lane,
            'status': status,
        })

    event.status = event.Status.FINISHED
    event.save()

    return results


def form_heats_for_competition(competition):
    """
    Формирует заплывы для всех категорий соревнования по порядку.
    """
    events = Event.objects.filter(
        competition=competition
    ).order_by('order')

    heat_number = 1
    for event in events:
        heat_number = form_heats_for_event(event, starting_heat_number=heat_number)

    competition.status = competition.Status.IN_PROGRESS
    competition.save()