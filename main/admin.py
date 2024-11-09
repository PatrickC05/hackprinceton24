from django.contrib import admin
from main.models import User, Goal, GoalDay, Journal, Therapy

# Register your models here.
admin.site.register(User)
admin.site.register(Goal)
admin.site.register(GoalDay)
admin.site.register(Journal)
admin.site.register(Therapy)