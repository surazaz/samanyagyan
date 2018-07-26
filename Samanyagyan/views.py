import json
import time

from django.utils.safestring import mark_safe

from .firebase_config import *
from django.utils.translation import gettext_lazy as _


def sign(request):
    if request.method == "GET":
        return render(request, "source/login.html")
    else:
        email = request.POST.get("email")
        passw = request.POST.get("pass")
        try:
            user = authe.sign_in_with_email_and_password(email, passw)
            uid = user['localId']
            token = user['idToken']

            adminid_list = db.child('Users').child('Admin').shallow().get(token).val()
            schooladminid_list = db.child('Users').child('SchoolAdmin').shallow().get(token).val()
            studentid_list = db.child('Users').child('Student').shallow().get(token).val()
            parentid_list = db.child('Users').child('Parent').shallow().get(token).val()
            teacher_list = db.child('Users').child('Teacher').shallow().get(token).val()

            if uid in list(adminid_list):
                return redirect("companyadmin")
            elif uid in list(schooladminid_list):
                return redirect("schooladmin")
            elif uid in list(teacher_list):
                return redirect("teacher")
            elif uid in list(studentid_list):
                return redirect('student', uid=uid)
            elif uid in list(parentid_list):
                return redirect("parent")
            else:
                message = "You are not authoriized"
                return render(request, "source/login.html", {"messg": message})
        except:

            messages.warning(request, 'Invalid Credential!')
            return render(request, "source/login.html")


companyitems = ['Schools', 'SchoolAdmin', 'questions']
schoolitems = ['User', 'Courses']


def logout(request):
    user = authe.current_user
    # firebase.auth.signOut()
    del user['idToken']
    return sign(request)


def forgotpass(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            authe.send_password_reset_email(email)
            messages.success(request, '<h4 ">Instruction Sent ! </h4> '
                                      ' Password reset link have been sent to '
                                      '<b>' + email + '</b>'
                                                      '<br>Please check it!', extra_tags='safe')

        except:
            messages.warning(request, 'Invalid Email!')

    return render(request, "source/forgot.html")


def changepass(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        # user = authe.current_user
        try:
            authe.send_password_reset_email(email)
            messages.success(request, '<h4 ">Instruction Sent ! </h4> '
                                      ' Password reset link have been sent to '
                                      '<b>' + email + '</b>'
                                                      '<br>Please check it!', extra_tags='safe')

        except:
            messages.warning(request, 'Invalid Email!')

    return render(request, "source/changepass.html")


def verifyemail(request):
    user = authe.current_user
    authe.send_email_verification(user['idToken'])

    return HttpResponse("Helloo")


def userform(request, formtype, id=None):
    token = gettoken()
    if token:
        course_list = getnameidlist("Courses", "title", token)
        user_list = getusernamelist(formtype, token)
        gradelist = getnameidlist("Grade", "title", token)
        if formtype == 'Teacher':
            form = StaffForm()
            category = "Teacher"
        elif formtype == 'Student':
            form = StudentForm()
            category = "Student"
        elif formtype == 'Parent':
            form = ParentForm()
            category = "Parent"

        if id:
            try:
                forminstance = db.child("Users").child(formtype).child(id).get(token).val()
                if formtype == "Student":
                    form = EditStudentForm(forminstance)
                elif formtype == "Parent":
                    form = EditParentForm(forminstance)
                elif formtype == "Teacher":
                    form = EditStaffForm(forminstance)

            except:
                isupdate = 0
                return HttpResponse("id not valid")  # for adding new data into forms

        if request.method == 'POST':
            request.POST._mutable = True
            email = request.POST.get("email")
            passw = request.POST.get("password")
            r = request.POST

            try:
                if form.is_valid:
                    del r['csrfmiddlewaretoken']
                    if id:
                        r['updated_at'] = time.time()
                        db.child("Users").child(formtype).child(id).update(r, token)
                        messages.success(request, _("Updated Successfully"))
                        return redirect("userform", formtype)

                    try:
                        del r['password']
                    except:
                        pass
                    user = authe.create_user_with_email_and_password(email, passw)
                    uid = user['localId']
                    r['created_at'] = time.time()
                    db.child("Users").child(category).child(uid).set(r, token)
                    db.child("Grade").child(r["grade"]).child("Student").update({uid: "true"}, token)
                    messages.success(request, _("Added Succesfully"))
                    return redirect('/mainapp/source/schooladmin/')
            except:
                message = "Unable to create account. Please try again"
                return render(request, "source/schooladmin.html", {"messg": message})

        try:
            gradeid = db.child('Users').child(formtype).child(id).child('grade').get(token).val()
        except:
            pass
        args = {'form': form, 'items': schoolitems, 'formtype': formtype, 'grade': gradelist, 'user_list': user_list,
                'editid': id,
                'gradeid': gradeid, 'course_list': course_list}
        return render(request, "source/form.html", args)
    else:
        return sign(request)


def allform(request, formtype, id=None):
    token = gettoken()
    if token:
        user_list = getusernamelist(formtype, token)
        all_list = getnameidlist(formtype, "title", token)
        gradelist = getnameidlist("Grade", "title", token)
        course_list = getnameidlist("Courses", "title", token)

        class AllForm(forms.ModelForm):
            class Meta:
                model = getform(formtype)
                fields = '__all__'

        if id:
            try:
                if formtype == 'SchoolAdmin':
                    forminstance = db.child("Users").child(formtype).child(id).get(token).val()
                    form = EditSchoolAdminForm(forminstance)

                elif formtype == 'Courses':
                    gradeid = db.child(formtype).child(id).child('grade').get(token).val()
                    gradetitle = db.child("Grade").child(gradeid).child("title").get(token).val()
                    forminstance = db.child(formtype).child(id).get(token).val()
                    form = EditCourseForm(forminstance)
                    if request.method == 'POST':
                        request.POST._mutable = True
                        r = request.POST
                        r['updated_at'] = time.time()
                        del r['csrfmiddlewaretoken']
                        db.child(formtype).child(id).update(r, token)
                        messages.success(request, _("Updated Succesfully"))
                        return redirect("allform", formtype)
                    return render(request, "source/courseform.html",
                                  {'form': form, 'course_list': course_list, 'formtype': formtype,
                                   'items': schoolitems, 'grade': gradetitle, 'gradelist': gradelist})

                else:
                    forminstance = db.child(formtype).child(id).get(token).val()
                    form = AllForm(forminstance)

            except:
                isupdate = 0
                return HttpResponse("id not valid")  # for adding new data into forms

        else:
            form = AllForm()

        if request.method == 'POST':
            form = AllForm(request.POST)
            request.POST._mutable = True
            email = request.POST.get("email")
            passw = request.POST.get("password")
            r = request.POST
            del r['csrfmiddlewaretoken']
            try:
                gid = r['grade']
                gradename = db.child("Grade").child(gid).child("title").get(token).val()
                r["title"] = gradename + ": " + r["title"]
            except:
                pass
            if form.is_valid:
                # update if request.post has id
                if id:
                    r['updated_at'] = time.time()
                    if formtype == 'SchoolAdmin':
                        db.child("Users").child(formtype).child(id).update(r, token)
                    else:
                        db.child(formtype).child(id).update(r, token)
                    messages.success(request, _("Updated Successfully"))
                    return redirect("allform", formtype=formtype)

                else:
                    # for creating schooladmin if not exist
                    if formtype == 'SchoolAdmin':
                        del r['password']
                        r['created_at'] = time.time()
                        user = authe.create_user_with_email_and_password(email, passw)
                        uid = user['localId']
                        db.child("Users").child("SchoolAdmin").child(uid).set(r, token)
                        messages.success(request, _("Added Succesfully"))

                    else:
                        # insert if request.post doesnt have id
                        r['created_at'] = time.time()
                        cid = db.child(formtype).push(r, token)
                        courseid = cid["name"]
                        try:  # For pushing only courseid in grade node
                            # db.child("Schools").push(r,token)
                            db.child("Grade").child(r["grade"]).child("Courses").update({courseid: "true"}, token)
                            db.child("Courses").child(courseid).update({r["grade"]}, token)
                            messages.success(request, _("Update Successfully"))
                            return redirect("/mainapp/allform/Courses/")
                        except:
                            pass

        if formtype == 'Schools':
            items = companyitems

        elif formtype == 'SchoolAdmin':
            items = companyitems

        else:
            items = schoolitems

        args = {'form': form, 'items': items, 'formtype': formtype, 'all_list': all_list, 'grade': gradelist,
                'user_list': user_list, 'course_list': course_list, 'editid': id}
        return render(request, 'source/form.html', args)
    else:
        return sign(request)


def companyadmin(request):
    token = gettoken()
    if token:
        return render(request, 'source/companyadmin.html', {'items': companyitems})
    else:
        return sign(request)


def schooladmin(request):
    token = gettoken()
    if token:

        return render(request, 'source/schooladmin.html', {'items': schoolitems})
    else:
        return sign(request)


def studentview(request, uid):
    token = gettoken()
    if token:
        x = authe.current_user
        uid = (x['localId'])
        # courselist=student_course(x['localId'])
        return render(request, 'source/student.html', {'uid': uid})
    else:
        return sign(request)


def parent(request):
    token = gettoken()
    if token:
        x = authe.current_user
        return render(request, 'source/parent.html')
    else:
        return sign(request)


def editprofile(request):
    user = authe.current_user
    token = gettoken()
    if token:
        uid = user['localId']
        forminstance = db.child("Users").child("SchoolAdmin").child(uid).get(token).val()
        if forminstance:
            form = EditSchoolAdminForm(forminstance)
            myhtml = 'adminbase.html'
            if request.method == 'POST':
                request.POST._mutable = True
                r = request.POST
                r['updated_at'] = time.time()
                db.child("Users").child("SchoolAdmin").child(uid).update(r, token)
                messages.success(request, _("Update Successfully"))
            return render(request, "source/edit.html",
                          {'form': form, 'myhtml': myhtml, 'uid': uid, 'items': schoolitems})

        else:
            forminstance = db.child("Users").child("Teacher").child(uid).get(token).val()
            if forminstance:
                form = EditStaffForm(forminstance)
                myhtml = 'teacherbase.html'
                if request.method == 'POST':
                    request.POST._mutable = True
                    r = request.POST
                    r['updated_at'] = time.time()
                    db.child("Users").child("Teacher").child(uid).update(r, token)
                    messages.success(request, _("Update Successfully"))
                return render(request, "source/edit.html", {'form': form, 'myhtml': myhtml, 'uid': uid})
            else:
                forminstance = db.child("Users").child("Student").child(uid).get(token).val()
                if forminstance:
                    form = EditStudentForm(forminstance)
                    myhtml = 'sidebarbase.html'
                    if request.method == 'POST':
                        request.POST._mutable = True
                        r = request.POST
                        r['updated_at'] = time.time()
                        db.child("Users").child("Student").child(uid).update(r, token)
                        messages.success(request, _("Update Successfully"))
                    return render(request, "source/edit.html", {'form': form, 'myhtml': myhtml, 'uid': uid})
                else:
                    forminstance = db.child("Users").child("Parent").child(uid).get(token).val()
                    if forminstance:
                        form = EditStudentForm(forminstance)
                        myhtml = 'sidebarbase.html'
                        if request.method == 'POST':
                            request.POST._mutable = True
                            r = request.POST
                            r['updated_at'] = time.time()
                            db.child("Users").child("Parent").child(uid).update(r, token)
                            messages.success(request, _("Update Successfully"))
                        return render(request, "source/edit.html", {'form': form, 'myhtml': myhtml, 'uid': uid})
    else:
        return sign(request)


# Tab Quiz

def tabquiz(request):
    token = gettoken()
    if token:
        user=authe.current_user
        uid=user['localId']
        courselist = student_course(uid, token)
        return render(request, "source/tabquiz.html", {'courselist': courselist})
    else:
        return sign(request)


def takequiz(request,quizid):
    token = gettoken()
    if token:
        user=authe.current_user
        uid=user['localId']
        attempt = db.child("Results").child(uid).child(quizid).push({'quiz_time': '0'}, token)
        attempt_id = attempt['name']
        db.child("Results").child(uid).child(quizid).child(attempt_id).update({'total_correctans': 0}, token)
        deadline = getdeadline('Quiz', quizid, 'deadline', token)
        question_list = list(getrelation("Quiz", quizid, "Questions", "question", token))
        no_of_questions = len(question_list)
        db.child("Results").child(uid).child(quizid).child(attempt_id).update({'total_questions': no_of_questions}, token)
        json_data = mark_safe(json.loads(json.dumps(question_list)))
        return render(request, "source/takequiz.html",
                      {'question_list': question_list, 'deadline': deadline,
                       'json_data': json_data, 'quizid': quizid, 'attempt_id': attempt_id})
    else:
        return sign(request)


def quizlist(request):
    return render(request, "source/quizlist.html")


def coursequiz(request, cid):
    token = gettoken()
    if token:
        quizlist = getrelation("Courses", cid, 'Quiz', 'title', token)
        return render(request, "source/coursequiz.html", {'quizlist': quizlist})
    else:
        return sign(request)


# for grade
def grade(request):
    token = gettoken()
    if token:
        gradelist = getnameidlist("Grade", "title", token)
        if request.method == 'POST':
            request.POST._mutable = True
            r = request.POST
            r['created_at'] = time.time()
            del r['csrfmiddlewaretoken']
            db.child("Grade").push(r, token)
            messages.success(request, _("Added Succesfully"))
            return redirect("/mainapp/grade/")
        args = {'items': schoolitems, 'grade': gradelist}
        return render(request, "source/grade.html", args)
    else:
        return sign(request)


# For Assigning teacher to courses
def assign(request):
    token = gettoken()
    if token:
        teacher_list = getusernamelist("Teacher", token)
        course_list = getnameidlist("Courses", "title", token)
        args = {'course_list': course_list, 'teacher_list': teacher_list, 'items': schoolitems}
        if request.method == 'POST':
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']
            db.child("Users").child("Teacher").child(r["teacher"]).child("Courses").update({r["course"]: "true"}, token)
            db.child("Courses").child(r["course"]).child("Teacher").update({r["teacher"]: "true"}, token)
            return redirect("schooladmin")

        return render(request, "source/assigncourse.html", args)
    else:
        return sign(request)


def viewcourse(request, id=None):
    token = gettoken()
    if token:
        getcid_items = getrelation("Grade", id, "Courses", "title", token)
        return render(request, "source/viewcourse.html", {'getcid_items': getcid_items, 'items': schoolitems})
    else:
        return sign(request)


# views for teacher
def teacherview(request):
    user = authe.current_user
    token = gettoken()
    if token:
        uid = user['localId']
        return render(request, 'teacher/teacherhome.html', {'uid': uid})
    else:
        return sign(request)


def courses(request, courseid=None):
    user = authe.current_user
    token = gettoken()
    if token:
        uid = user['localId']
        coursedetail = teacher_relation(uid, "Courses", token)

        if request.method == 'POST':
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']
            r['created_at'] = time.time()
            cid = r['course']
            topicid = db.child("Topics").push(r, token)
            tid = topicid['name']
            # db.child('Topics').child(tid).child('Courses').update({cid: 'true'}, token)
            db.child("Courses").child(cid).child('Topics').update({tid: 'true'}, token)
            template = '/mainapp/teacher/courses/' + str(cid) + '/'

            return redirect(template, uid=uid)
        if courseid:
            topicdetail = getrelation("Courses", courseid, "Topics", "title", token)
            return render(request, 'teacher/courses.html',
                          {'courses': list(coursedetail), 'topics': (topicdetail), 'uid': uid})
        return render(request, 'teacher/courses.html', {'courses': list(coursedetail), 'uid': uid})
    else:
        return sign(request)


def quizcreate(request):
    token = gettoken()
    if token:
        user = authe.current_user
        uid = user['localId']
        coursedetail = getnameidlist("Courses", "title", token)
        topicdetail = getnameidlist("Topics", "title", token)
        if request.method == 'POST':
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']
            if r['type'] == 'Training':
                del r['deadline']
            r['created_at'] = time.time()

            x = db.child('Quiz').push(r, token)
            quizid = x['name']
            db.child("Courses").child(r['course']).child('Quiz').update({quizid: 'true'}, token)
            db.child("Users").child("Teacher").child(uid).child('Quiz').update({quizid: 'true'}, token)
            db.child("Quiz").child(quizid).update({"Teacher": uid}, token)
            db.child("Topics").child(r['topic']).child('Quiz').update({quizid: 'true'}, token)
            return redirect('quizquestion', quizid=quizid)

        return render(request, 'teacher/quizcreate.html', {'courses': coursedetail, 'topics': topicdetail})
    else:
        return sign(request)


def quizquestion(request, quizid):
    token = gettoken()
    if token:
        quizquestionlist = getrelation('Quiz', quizid, 'Questions', 'question', token)
        quizcourse = db.child("Quiz").child(quizid).child("course").get(token).val()
        quiztopic = db.child("Quiz").child(quizid).child("topic").get(token).val()
        allquestionlist = getrelation("Courses", quizcourse, "Questions", "question", token)
        if request.method == "POST":
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']
            r['course'] = quizcourse
            r['topic'] = quiztopic
            # if questionid then update
            try:
                qid = r['questionid']
                if r['type'] == 'mcq':
                    ca = r['correctanswer']
                    r['correctanswer'] = r[ca]
                else:
                    del r['option1']
                del r['questionid']
                r['updated_at'] = time.time()
                db.child('Questions').child(qid).update(r, token)
                data = {'question': r['question'], 'qid': qid}
                messages.success(request, _("Question Updated Succesfully"))
                return redirect('question')
            except:  # creating new question#qid=questionid
                if r['type'] == 'mcq':
                    ca = r['correctanswer']
                    r['correctanswer'] = r[ca]
                else:
                    del r['option1']

                r['created_at'] = time.time()
                z = db.child('Questions').push(r, token)
                qid = z['name']
                # reverse relation for quiz and question
                db.child('Quiz').child(quizid).child('Questions').update({qid: 'true'}, token)
                db.child('Courses').child(quizcourse).child('Questions').update({qid: 'true'}, token)
                db.child('Topics').child(quiztopic).child('Questions').update({qid: 'true'}, token)
                data = {'question': r['question'], 'qid': qid}
            return redirect('quizquestion', quizid)
        args = {'quizid': quizid, 'questionlist': quizquestionlist, 'allquestionlist': allquestionlist}
        return render(request, 'teacher/question.html', args)
    else:
        return sign(request)


def question(request):
    user = authe.current_user
    token = gettoken()
    if token:
        teacher_list = db.child('Users').child('Teacher').shallow().get(token).val()
        companyadmin_list = db.child('Users').child('Admin').shallow().get(token).val()
        uid = user['localId']
        questionlist = getnameidlist("Questions", "question", token)

        if request.method == "POST":
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']
            # if questionid then update
            try:

                qid = r['questionid']
                if r['type'] == 'mcq':
                    ca = r['correctanswer']
                    r['correctanswer'] = r[ca]
                else:
                    del r['option1']
                r['updated_at'] = time.time()
                del r['questionid']
                db.child('Questions').child(qid).update(r, token)
                data = {'question': r['question'], 'qid': qid}
                messages.success(request, ("Question Updated Succesfully"))
                return redirect('question')

            except:  # creating new question#qid=questionid
                if r['type'] == 'mcq':
                    ca = r['correctanswer']
                    r['correctanswer'] = r[ca]
                else:
                    del r['option1']

                r['created_at'] = time.time()
                z = db.child('Questions').push(r, token)
                qid = z['name']
                db.child("Courses").child(r['course']).child("Questions").update({qid: 'true'}, token)
                db.child("Topics").child(r['topic']).child("Questions").update({qid: 'true'}, token)
                data = {'question': r['question'], 'qid': qid}
                messages.success(request, _("Question Added Succesfully"))
            return redirect('question')

        if uid in list(companyadmin_list):
            coursedetail = list(getnameidlist("Courses", 'title', token))
            topicdetail = list(getnameidlist("Topics", 'title', token))
            args = {'questionlist': questionlist, 'courses': coursedetail, 'items': companyitems, 'topics': topicdetail}
            return render(request, 'source/companyquestion.html', args)
        else:
            coursedetail = list(teacher_relation(uid, "Courses", token))
            topicdetail = list(getnameidlist("Topics", 'title', token))
            args = {'questionlist': questionlist, 'courses': coursedetail, 'topics': topicdetail}
            return render(request, 'teacher/rawquestion.html', args)

        # return render(request, 'teacher/question.html', {'questionlist': questionlist, 'myhtml': myhtml})
    else:
        return sign(request)


def delete(request, deleteid):
    token = gettoken()
    if token:
        if request.method == "GET" and request.is_ajax():
            qcourse = db.child('Questions').child(deleteid).child('course').get(token).val()
            qtopic = db.child('Questions').child(deleteid).child('topic').get(token).val()
            db.child('Questions').child(deleteid).remove(token)
            db.child('Courses').child(qcourse).child("Questions").child(deleteid).remove(token)
            db.child('Topics').child(qtopic).child("Questions").child(deleteid).remove(token)
            db.child('Questions').child(deleteid).remove(token)
            return HttpResponse("Question deleted succesfully")
    else:
        return sign(request)


def remove_from_quiz(request, quizid, qid):
    token = gettoken()
    if token:
        if request.method == "GET" and request.is_ajax():
            db.child('Quiz').child(quizid).child('Questions').child(qid).remove(token)
            return HttpResponse("Question deleted succesfully")
    else:
        return sign(request)


def questiondetail(request, questionid):
    token = gettoken()
    if token:
        if request.method == "GET" and request.is_ajax():
            detail = db.child('Questions').child(questionid).get(token).val()
            return JsonResponse(detail)
    else:
        return sign(request)


def coursetopic(request, courseid):
    token = gettoken()
    if token:
        if request.method == "GET" and request.is_ajax():
            topicdetail = db.child('Courses').child(courseid).child('Topics').get(token).val()
            return JsonResponse(topicdetail)
    else:
        return sign(request)


def classes(request):
    return render(request, 'teacher/classes.html')


def students(request):
    return HttpResponse("HELLO")


def add_to_quiz(request, quizid, qid):
    token = gettoken()
    if token:
        db.child("Quiz").child(quizid).child('Questions').update({qid: 'true'}, token)
        return HttpResponse('Question added to quiz')
    else:
        return sign(request)


def teacherquizlist(request):
    token = gettoken()
    user = authe.current_user
    if token:
        uid = user['localId']
        quizlist = teacher_relation(uid, "Quiz", token)
        return render(request, "teacher/teacherquizlist.html", {'quizlist': quizlist})
    else:
        return sign(request)

def getworkout():
    import datetime
    current = datetime.datetime.now()
    x=current.hour
    workout_time=""
    if x>=4 and x<=9:
        workout_time="morning"
    elif x>=10 and x<=15:
        workout_time="afternoon"
    if x>=16 and x<=21:
        workout_time="evening"
    if x>=22 and x<=3:
        workout_time="night"
    return workout_time

def submitanswer(request, quizid, qid, attempt_id):
    token = gettoken()
    if token:
        user = authe.current_user
        uid = user['localId']
        std_info=db.child("Users").child("Student").child(uid).get(token).val()
        mark=db.child("Results").child(uid).child(quizid).child(attempt_id).child('total_correctans').get(token).val()
        no_of_correctans = int(mark)
        print(no_of_correctans)
        if request.method == "POST" and request.is_ajax:
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']

            correctans = db.child("Questions").child(qid).child('correctanswer').get(token).val()
            questype = db.child("Questions").child(qid).child('type').get(token).val()

            if questype == "subjective":
                data = "this is a subjective question"
                iscorrect=""
            else:
                if correctans == r['answer']:
                    data = "you are correct"
                    db.child("Results").child(uid).child(quizid).child(attempt_id).update({'total_correctans':no_of_correctans + 1},token)
                    iscorrect=1
                else:
                    data = "You are incorrect....The correct answer is" + correctans
                    iscorrect=0


            db.child("Results").child(uid).child(quizid).child(attempt_id).child(qid).update(r, token)
            #for workout time

            quesans={
                "quizattempt":attempt_id,
                "student_id":uid,
                "time_taken":r['time_taken'],
                "workout_time":getworkout(),
                "iscorrect":iscorrect,
                "questionid":qid,
                "gender":std_info['gender'],
                "special_care_needed":std_info['special_care_needed'],
                "subject_of_interest":std_info['subject_of_interest'],
                "grade":std_info['grade'],

            }
            db.child('Evaluations').push(quesans,token)
        return HttpResponse(data)
    else:
        return sign(request)



def time_taken(request, quizid, timetaken, attempt_id):
    token = gettoken()
    if token:
        user = authe.current_user
        uid = user['localId']
        db.child("Results").child(uid).child(quizid).child(attempt_id).update({'quiz_time': timetaken}, token)
        no_of_correctanswer = db.child("Results").child(uid).child(quizid).child(attempt_id).child("total_correctans").get(token).val()
        print("coreect answer")
        print(no_of_correctanswer)
        total_questions = db.child("Results").child(uid).child(quizid).child(attempt_id).child("total_questions").get(token).val()
        print(total_questions)

        args = {'total_questions':total_questions, 'no_of_correctanswer':no_of_correctanswer, 'uid':uid}
        return render(request, "source/viewresults.html", args)
    else:
        return  sign(request)

def quiz_results(request):
    token = gettoken()
    if token:
        user = authe.current_user
        uid = user['localId']
        quiz_list = list(db.child("Results").child(uid).shallow().get(token).val())
        quizname = []
        for i in quiz_list:
            quizname.append(db.child("Quiz").child(i).child("title").get(token).val())
            print(quizname)
        return render(request, "source/quiz_results.html", {'quizname':quizname, 'uid':uid})
    else:
        return sign(request)

def solvequestions(request,qid):
    token = gettoken()
    if token:
        user = authe.current_user
        uid = user['localId']
        std_info=db.child("Users").child("Student").child(uid).get(token).val()
        if request.method == "POST" and request.is_ajax:
            request.POST._mutable = True
            r = request.POST
            del r['csrfmiddlewaretoken']

            correctans = db.child("Questions").child(qid).child('correctanswer').get(token).val()
            questype = db.child("Questions").child(qid).child('type').get(token).val()

            if questype == "subjective":
                data = "this is a subjective question"
                iscorrect=""
            else:
                if correctans == r['answer']:
                    data = "you are correct"
                    iscorrect=1
                else:
                    data = "You are incorrect....The correct answer is" + correctans
                    iscorrect=0
            #for workout time

            quesans={
                "quizattempt":"",
                "student_id":uid,
                "time_taken":r['time_taken'],
                "workout_time":getworkout(),
                "iscorrect":iscorrect,
                "questionid":qid,
                "gender":std_info['gender'],
                "special_care_needed":std_info['special_care_needed'],
                "subject_of_interest":std_info['subject_of_interest'],
                "grade":std_info['grade'],

            }
            db.child('Evaluations').push(quesans,token)
        return HttpResponse(data)
    else:
        return sign(request)

def justquestions(request,cid,tid=None):
    token = gettoken()
    if token:
        question_list = list(getrelation("Courses", cid, "Questions", "question", token))
        if tid:
            question_list = list(getrelation("Topics", tid, "Questions", "question", token))
        json_data = mark_safe(json.loads(json.dumps(question_list)))
        return render(request, "source/solvequestions.html",
                      {'question_list': question_list,
                       'json_data': json_data})
    else:
        return sign(request)