from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('study/', views.study_session, name='study_session'),
    path('study/<int:level>/', views.study_session, name='study_session_level'),
    path('study/action/<int:word_id>/<str:action>/', views.review_action, name='review_action'),
    path('words/', views.word_list, name='word_list'),
    path('init_user_words/', views.init_user_words, name='init_user_words'),
    path('words/hard/', views.hard_words, name='hard_words'),
    path('words/easy/', views.easy_words, name='easy_words'),
    path('study/hard/', views.study_hard_words, name='study_hard_words'),
    path('study/easy/', views.study_easy_words, name='study_easy_words'),
    path('grammar/', views.grammar_list, name='grammar_list'),
    path('grammar/level/<int:level>/', views.grammar_list, name='grammar_list_level'),
    path('grammar/<int:pk>/', views.grammar_detail, name='grammar_detail'),
    path('stats/', views.stats_view, name='stats'),
]
