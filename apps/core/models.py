from django.db import models



class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class PublishedModel(models.Model):
    is_published = models.BooleanField(default=False)

    class Meta:
        abstract = True

class SEOMixin(models.Model):
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        abstract = True