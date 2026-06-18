from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.competitions.utils import generate_application_template, parse_application_excel
from apps.competitions.models import Competition, Application


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