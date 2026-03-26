from django.contrib import admin
from main.models import User
from . import models

# Register your models here.

admin.site.register(User)
admin.site.register(models.Workshop)
admin.site.register(models.Workshop_groups)
admin.site.register(models.Workshop_designations)
admin.site.register(models.WorkshopVisitors)
admin.site.register(models.Feedback)
admin.site.register(models.FeedbackQuestion)