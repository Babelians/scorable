from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.create_score, name='create_score'),
    path('score/<int:pk>', views.score_detail, name='score_detail'),
    path('user/<int:pk>', views.user_detail, name='user_detail'),
] 