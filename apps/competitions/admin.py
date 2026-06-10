from django.contrib import admin
from apps.competitions.models import Competition, Event, Application, AthleteEvent, Heat, HeatLane
from apps.teams.models import Team, Athlete


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'status', 'is_open']
    list_filter = ['status', 'is_open']
    search_fields = ['name', 'location']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['competition', 'gender', 'birth_year_from', 'birth_year_to', 'distance', 'stroke', 'status']
    list_filter = ['competition', 'gender', 'stroke', 'status']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['competition', 'coach', 'status', 'created_at']
    list_filter = ['competition', 'status']


@admin.register(AthleteEvent)
class AthleteEventAdmin(admin.ModelAdmin):
    list_display = ['event', 'athlete', 'preliminary_time', 'is_paid']
    list_filter = ['event', 'is_paid']

@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    list_display = ['number', 'event', 'status']
    list_filter = ['event', 'status']

@admin.register(HeatLane)
class HeatLaneAdmin(admin.ModelAdmin):
    list_display = ['heat', 'lane', 'athlete_event', 'result_time', 'dns', 'dnf', 'dsq']

