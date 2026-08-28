from django.urls import path
from . import views

urlpatterns = [
    path('student_graph/', views.student_graph, name='student_graph'),  # Povezivanje sa view funkcijom
    path('sviStudentiISviProfesori', views.student_graph,name = 'student_graph'),
    path('zanimljivosti',views.student_graph,name = 'student_graph'),
    path('login',views.student_graph,name = 'login'),
    path('statistika', views.student_graph,name = 'student_graph'),
    path('students_form', views.student_graph,name = 'student_graph'),
    path('login/', views.login_view, name='login'),
    path('zanimljivosti/', views.zanimljivosti, name='zanimljivosti'),
]
