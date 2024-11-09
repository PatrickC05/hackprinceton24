from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=10, null=True)
    therapyscale = models.IntegerField(null=True)

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=1)

    def __str__(self):
        return self.name

class GoalDay(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.goal.name} - {self.date}"
    

class Journal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    entry = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"