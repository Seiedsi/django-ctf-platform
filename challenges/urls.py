from django.urls import path
from . import views
from .views import challenge_list


urlpatterns = [
    path("", challenge_list, name="challenge_list"),
    path('spawn/<int:pk>/', views.spawn_challenge, name='spawn_challenge'),
    path('stop/<int:pk>/', views.stop_challenge, name='stop_challenge'),
    path('<int:pk>/', views.challenge_detail, name='challenge_detail'),
]
