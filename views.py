import pyrebase
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import auth

# Create your views here.
# from rest_framework.templatetags.rest_framework import items
from django.views.generic.base import View

from mainapp.forms import SchoolModelForm, StudentForm, ParentForm, StaffForm
from mainapp.models import School, Course

config = {
    'apiKey': "AIzaSyCrAG2_pI8A00gIAPBniRLqv7Kym2d97f0",
    'authDomain': "fir-project-8cea6.firebaseapp.com",
    'databaseURL': "https://fir-project-8cea6.firebaseio.com",
    'projectId': "fir-project-8cea6",
    'storageBucket': "fir-project-8cea6.appspot.com",
    'messagingSenderId': "609798741798"
}
firebase = pyrebase.initialize_app(config)

authe = firebase.auth()
db = firebase.database()
storage = firebase.storage()

userdata = db.child("Users").get().val()
schooldata=db.child("Schools").get().val()
# courses=db.child("")
# myObj = {
#     "name":"John",
#     "age":30,
#     "cars": {
#         "car1":"Ford",
#         "car2":"BMW",
#         "car3":"Fiat"
#     }
#  }
# db.child("Mydata").push(myObj)


def sign(request):
    return render(request, "source/login.html")


companyitems = ['Schools']
schoolitems = ['User','Courses']

def postsign(request):
    email = request.POST.get("email")
    passw = request.POST.get("pass")
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
        uid = user['localId']
        adminid_list = (list(db.child('Users').child('Admin').shallow().get().val()))
        schooladminid_list = (list(db.child('Users').child('SchoolAdmin').shallow().get().val()))
        # parentid_list = (list(db.child('Users').child('Parent').shallow().get().val()))
        # studentid_list = (list(db.child('Users').child('Student').shallow().get().val()))
        if uid in adminid_list:
            # print(user['idToken'])
            session_id = user['idToken']
            request.session['uid'] = str(session_id)
            print(session_id)
            print(request.session['uid'])
            return render(request, "source/companyadmin.html", {'items':companyitems})
        elif uid in schooladminid_list:
            return render(request, "source/schooladmin.html",{'items':schoolitems})
        # elif uid in parentid_list:
        #     return render(request, "source/parent.html")
        # elif uid in studentid_list:
        #     return render(request, "source/student.html")
        else:
            message = "You are not authoriized"
            return render(request, "source/login.html", {"messg": message})
    except RuntimeError:
        pass
        # message = "Invalid Credentials"
        # print(message)
        # return render(request, "source/login.html", {"messg": message})



def logout(request):
    # auth.logout(request)
    return sign(request)


# def schoolform(request):
#     form = SchoolModelForm()
#
#     if request.method == 'POST':
#         request.POST._mutable = True
#         r = request.POST
#         print(r)
#         try:
#             if form.is_valid:
#                 form = SchoolModelForm(request.POST)
#                 del r['csrfmiddlewaretoken']
#                 print(r)
#                 db.child("Schools").push(r)
#                 return render(request, 'source/companyadmin.html')
#         except RuntimeError:
#             pass
#
#     return render(request, "source/form.html", {'form': form})


# User Form

def getusernamelist(which):
    data=userdata
    idlist = list(data[which].keys())
    student_namelist = []
    for i in idlist:
        student_namelist.append(data[which][i]['name'])
    return zip(idlist, student_namelist)




def userform(request, formtype):
    if formtype == 'staff':
        form = StaffForm()
        category = "Staff"
    elif formtype == 'student':
        form = StudentForm()
        category = "Student"
    elif formtype == 'parent':
        form = ParentForm()
        category = "Parent"

    if request.method == 'POST':
        print(request.POST)
        request.POST._mutable = True
        email = request.POST.get("email")
        passw = request.POST.get("password")
        r = request.POST
        print(r)

        try:
            if form.is_valid:
                del r['csrfmiddlewaretoken']
                print(r)
                user = authe.create_user_with_email_and_password(email, passw)
                uid = user['localId']
                print(uid)
                db.child("Users").child(category).child(uid).set(r)
                return redirect('source/schooladmin.html')

        except:
            message = "Unable to create account. Please try again"
            return render(request, "source/schooladmin.html", {"messg": message})

    args = {'form': form, 'items': schoolitems, 'formtype':formtype}
    return render(request, "source/form.html", args)


def getnameidlist(which, suitablename):
   try:
       mydata = db.child(which).get().val()

       idslist = list(mydata.keys())
       print(idslist)
       nameslist = []
       for i in idslist:
           nameslist.append(mydata[i]['details'][suitablename])
       print(nameslist)
       return zip(idslist, nameslist)
   except:
       pass


def getform(formtype):
   if formtype == 'Schools':
       modelform = School
       comb_list = []

   elif formtype == 'Courses':
       modelform = Course
       # comb_list = getnameidlist("Programs", "title")

   return (modelform)


def allform(request, formtype, id=None):
   class AllForm(forms.ModelForm):
       class Meta:
           model = getform(formtype)
           fields = '__all__'
   if id:
       try:
           forminstance = db.child(formtype).child(id).get().val()
           form = AllForm(forminstance)

       except:
           isupdate = 0
           return HttpResponse("id not valid")  # for adding new data into forms
   else:
       form = AllForm()

   if request.method == 'POST':
       form = AllForm(request.POST)
       request.POST._mutable = True
       r=request.POST
       del r['csrfmiddlewaretoken']

       if form.is_valid:
           # update if request.post has id
           if id:
               db.child(formtype).child(id).update(r)
           else:
               # insert if request.post doesnt have id
               db.child(formtype).push(r)


   if formtype == 'Schools':
       items =companyitems
   else:
       items = schoolitems

   args = {'form': form, 'items': items, 'formtype':formtype}
   return render(request, 'source/form.html', args)

def companyadmin(request):
    return render(request, 'source/companyadmin.html',{'items':companyitems})

def schooladmin(request):
    return render(request, 'source/schooladmin.html',{'items':schoolitems})
#views for teacher
class TeacherView(View):

    initial = {'key': 'value'}
    template_name = 'Teacher/teacherhome.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    # return render(request, self.template_name, {'form': form})
def students(request):
    std_name_idlist=getusernamelist("Student")
    arg={'stdlist':std_name_idlist}
    return render(request,'Teacher/students.html',arg)
def courses(request):
    return render(request,'Teacher/courses.html')
def quiz(request):
    import json
    if request.method=="POST":
        x=json.dumps(request.POST)
        y=json.loads(x)
        print(x)
        print(y)
        db.child('Quiz').push(x)
        db.child('Quiz').push(y)
    return render(request,'Teacher/quiz1.html')
def classes(request):
    return render(request,'Teacher/classes.html')