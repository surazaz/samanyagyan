from django.urls import path
from mainapp import views

urlpatterns = [
    path('sign/', views.sign, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('allform/<str:formtype>/', views.allform, name='allform'),
    path('allform/<str:formtype>/<str:id>/', views.allform, name='allform'),
    path('userform/<str:formtype>/', views.userform, name='userform'),
    path('userform/<str:formtype>/<str:id>/', views.userform, name='userform'),
    path('source/companyadmin/', views.companyadmin, name='companyadmin'),
    path('source/parent/', views.parent, name='parent'),
    path('source/schooladmin/', views.schooladmin, name='schooladmin'),
    path('source/student/<str:uid>/', views.studentview, name='student'),
    path('allform/<str:formtype>/<str:id>/', views.allform, name='allform'),
    path('teacher/', views.teacherview, name='teacher'),
    path('teacher/courses/', views.courses, name='courses'),
    path('teacher/courses/<str:courseid>/', views.courses, name='courses'),
    path('teacher/students/', views.students, name='students'),
    path('teacher/questioncreate/<str:quizid>/', views.quizquestion, name='quizquestion'),
    path('teacher/questioncreate/', views.question, name='question'),
    path('teacher/classes/', views.classes, name='classes'),
    path('teacher/quizcreate/', views.quizcreate, name='quizcreate'),

    path('editprofile/', views.editprofile, name='editprofile'),
    path('verify/', views.verifyemail, name='verify'),
    path('forgot/', views.forgotpass, name='forgot'),
    path('change/', views.changepass, name='change'),

    # For Quiz
    path('quiz/', views.tabquiz, name='tabquiz'),
    # path('quiz/', views.tabquiz, name='tabquiz'),
    path('takequiz/<str:quizid>/', views.takequiz, name='takequiz'),
    path('justquestions/<str:cid>/', views.justquestions, name='justquestions'),
    # path('takequiz/<str:uid>/<str:cid>/', views.takequiz, name='takequiz'),
    # path('quizlist/', views.quizlist, name='quizlist'),
    path('coursequiz/<str:cid>/', views.coursequiz, name='coursequiz'),
    path('teacher/quizlist/', views.teacherquizlist, name='teacherquizlist'),

    # For Schooladmin
    path('grade/', views.grade, name='grade'),

    # For Assigning teacher
    path('assign/', views.assign, name='assign'),

    # for showing particular course of particulat grade
    path('viewcourse/<str:id>/', views.viewcourse, name='viewcourse'),
    path('delete/<str:deleteid>/', views.delete, name='deletequestion'),
    path('details/<str:questionid>/', views.questiondetail, name='questiondetail'),

    path('add_to_quiz/<str:quizid>/<str:qid>/',views.add_to_quiz,name="add_to_quiz"),
    path('remove_from_quiz/<str:quizid>/<str:qid>/',views.remove_from_quiz,name="add_to_quiz"),

    path('answer/<str:quizid>/<str:qid>/<str:attempt_id>/',views.submitanswer,name="submitanswer"),
    path('solvequestions/<str:qid>/',views.solvequestions,name="solvequestions"),
    path('<str:quizid>/<str:timetaken>/<str:attempt_id>/',views.time_taken,name="time_taken"),
    path('quizresults/',views.quiz_results,name="quiz_result"),

]

