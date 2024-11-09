from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('goals/', views.goals, name='goals'),
    path('therapy/', views.therapy, name='therapy'),
    path('new_goal/', views.new_goal, name='new_goal')
]
