from django.contrib import admin
from apps.teams.models import Team, Athlete


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'coach']
    search_fields = ['name', 'city']


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'birth_year', 'gender', 'team', 'coach']
    list_filter = ['gender', 'team']
    search_fields = ['last_name', 'first_name']