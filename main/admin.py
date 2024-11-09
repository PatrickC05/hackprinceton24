from django.contrib import admin
from main.models import User, Goal, GoalDay, Journal

# Register your models here.
admin.site.register(User)
admin.site.register(Goal)
admin.site.register(GoalDay)
admin.site.register(Journal)