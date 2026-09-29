from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("prueba/", views.prueba, name="prueba"),
    path("api/<int:question_id>/", views.QuestionDetailAPI.as_view(), name="question-detail-api"),
    path("api/<int:question_id>/vote/", views.VoteAPI.as_view(), name="vote-api"),
    path("api/login/", views.LoginAPI.as_view(), name="login-api"),
    path("api/polls/", views.QuestionListAPI.as_view(), name="question-list-api"),
    path("api/<int:question_id>/stats/", views.QuestionStatsAPI.as_view(), name="question-stats-api"), 
    path("api/<int:question_id>/delete/", views.QuestionDeleteAPI.as_view(), name="question-delete-api"),     
]