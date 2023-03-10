from django.urls import path
from . import views


app_name = 'logs'

urlpatterns = [
    path('answerlog/', views.answerlog, name='answerlog'),
    path('recbuttonlog/', views.recbuttonlog, name='recbuttonlog'),
    path('user_eval/',views.eval_log,name='evallog'),
    path('user_scrap/', views.user_scrap, name='userscrap'),
    path('total/answerlog/',views.answer_log_total,name='answer_total'),
    path('total/recommendlog/',views.recommend_log_total,name='recommend_total'),
    path('total/evallog/',views.eval_log_total,name='eval_total'),
]