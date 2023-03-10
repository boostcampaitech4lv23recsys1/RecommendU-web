from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # path('init/', views.db_first),
    # path('init2/', views.docu_answer_init),
    path('main/', views.main, name='main'),
    # path('search/', views.search_company),
    path('answers/', views.answer_recommend, name='answer_recommend'),  # POST : 프론트에서 유저정보/질문맥락 받아서 inference 진행 후 자소서 담아서 보내주기  => asnwer serializer
    path('page_change/', views.page_change, name="page_change"),
    path('check_status/', views.check_status, name='check_status'),
    path('document_total/',views.document_total,name='document_total'),
    path('answer_total/',views.answer_total,name='answer_total'),
    path('document_refresh/',views.document_refresh),
    path('answer_refresh/',views.answer_refresh),
    path('job_total/',views.job_total,name='job_total'),
    path('save_model/',views.save_model),
    path('save_embedding/',views.save_embedding),
    path('save_refresh/',views.save_refresh_data),
]