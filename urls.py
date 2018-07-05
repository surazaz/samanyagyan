from django.urls import path
from mainapp import views

urlpatterns = [
    path('sign/', views.sign, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('postsign/', views.postsign, name='login'),
    path('allform/<str:formtype>/', views.allform,name='allform'),
    path('allform/<str:formtype>/<str:id>', views.allform,name='allform'),
    # path('schoolform/', views.schoolfo, name='schoolform'),
    path('userform/<str:formtype>/', views.userform, name='userform'),
    path('companyadmin/', views.companyadmin, name='companyadmin'),
    path('schooladmin/', views.schooladmin, name='schooladmin'),
    path('teacher/home/', views.TeacherView.as_view(), name='home'),
    path('teacher/courses', views.courses, name='courses'),
    path('teacher/students', views.students, name='students'),
    path('teacher/quiz', views.quiz, name='quiz'),
    path('teacher/classes', views.quiz, name='classes'),


]
