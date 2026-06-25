from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.competitions.utils import generate_application_template, parse_application_excel
from apps.competitions.models import Competition, Application
from apps.competitions.services import form_heats_for_competition



class DownloadTemplateView(LoginRequiredMixin, View):

    def get(self, request, competition_id):
        wb = generate_application_template()
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="application_template.xlsx"'
        wb.save(response)
        return response


class UploadApplicationView(LoginRequiredMixin, View):

    def get(self, request, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)

        # Проверяем что приём заявок открыт
        if not competition.is_registration_open():
            messages.error(request, 'Приём заявок закрыт.')
            return redirect('/')
        return render(request, 'competitions/upload_application.html', {
            'competition': competition,
        })

    def post(self, request, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)

        print(f"FILES: {request.FILES}")
        print(f"POST: {request.POST}")

        excel_file = request.FILES.get('excel_file')
        print(f"excel_file: {excel_file}")

        if not excel_file:
            messages.error(request, 'Выберите файл для загрузки.')
            return render(request, 'competitions/upload_application.html', {
                'competition': competition,
            })

        # Проверяем что приём заявок открыт
        if not competition.is_registration_open():
            messages.error(request, 'Приём заявок закрыт.')
            return redirect('/')

        # Проверяем что файл загружен
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, 'Выберите файл для загрузки.')
            return render(request, 'competitions/upload_application.html', {
                'competition': competition,
            })

        # Создаём заявку
        application = Application.objects.create(
            competition=competition,
            coach=request.user,
            excel_file=excel_file,
        )

        # Парсим Excel
        result = parse_application_excel(excel_file, application)

        return render(request, 'competitions/upload_result.html', {
            'competition': competition,
            'success': result['success'],
            'errors': result['errors'],
            'athletes': result['athletes'],
        })



class FormHeatsView(LoginRequiredMixin, View):

    def post(self, request, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)

        form_heats_for_competition(competition)

        messages.success(request, 'Заплывы успешно сформированы.')
        return redirect('view_heats', competition_id=competition_id)


class ViewHeatsView(LoginRequiredMixin, View):

    def get(self, request, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)

        from apps.competitions.models import Heat
        heats = Heat.objects.filter(
            event__competition=competition
        ).select_related('event').prefetch_related(
            'heatlane_set__athlete_event__athlete'
        ).order_by('number')

        return render(request, 'competitions/view_heats.html', {
            'competition': competition,
            'heats': heats,
        })

class EnterResultsView(LoginRequiredMixin, View):

    def get(self, request, heat_id):
        from apps.competitions.models import Heat
        heat = get_object_or_404(Heat, id=heat_id)
        lanes = heat.heatlane_set.select_related(
            'athlete_event__athlete'
        ).order_by('lane')

        return render(request, 'competitions/enter_results.html', {
            'heat': heat,
            'lanes': lanes,
        })

    def post(self, request, heat_id):
        from apps.competitions.models import Heat, HeatLane
        from datetime import timedelta

        heat = get_object_or_404(Heat, id=heat_id)

        # Защита — нельзя менять результаты завершённого заплыва
        if heat.status == Heat.Status.FINISHED:
            messages.error(request, 'Заплыв уже завершён, результаты изменить нельзя.')
            return redirect('enter_results', heat_id=heat_id)

        lanes = heat.heatlane_set.all()

        for lane in lanes:
            lane_id = lane.id

            dns = request.POST.get(f'dns_{lane_id}') == 'on'
            dnf = request.POST.get(f'dnf_{lane_id}') == 'on'
            dsq = request.POST.get(f'dsq_{lane_id}') == 'on'
            time_str = request.POST.get(f'time_{lane_id}', '').strip()

            lane.dns = dns
            lane.dnf = dnf
            lane.dsq = dsq

            if time_str and not (dns or dnf or dsq):
                try:
                    parts = time_str.split(':')
                    minutes = int(parts[0])
                    seconds = float(parts[1])
                    lane.result_time = timedelta(
                        minutes=minutes,
                        seconds=int(seconds),
                        milliseconds=int(round((seconds % 1) * 100))
                    )
                except (ValueError, IndexError):
                    messages.error(request, f'Неверный формат времени на дорожке {lane.lane}')
                    return redirect('enter_results', heat_id=heat_id)
            else:
                lane.result_time = None

            lane.save()

        heat.status = Heat.Status.FINISHED
        heat.save()

        messages.success(request, f'Результаты заплыва {heat.number} сохранены.')
        return redirect('view_heats', competition_id=heat.event.competition.id)