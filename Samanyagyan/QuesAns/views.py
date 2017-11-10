from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import Question,UserAns
from .forms import NameForm,Userform

# Create your views here.
ob = Question.objects.all()
context_dict = {'ob':ob}
def home(request):
	
	return render(request,'home.html',context_dict)
	
def quiz(request):
    # if this is a POST request we need to process the form data
    data=""
    submitbutton= request.POST.get("submit")
  
        # create a form instance and populate it with data from the request
    form = NameForm(request.POST)
    


       # check whether it's valid:
    if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
        data= form.cleaned_data.get("answer")

        num= form.cleaned_data.get("number")
        z=Question.objects.get(id=num)
        if(z.ans.upper() == data.upper()):
        	r="CORRECT"
        else:
        	r="INCORRECT"


        context = {'form':form,'data':data,}
        return render(request,'quiz.html',{'ob':ob,'form':form,'data':data,'z':z,'num':num,'r':r})
    else:
    	return render(request, 'quiz.html',{'ob':ob,'form':form})	
      

    # if a GET (or any other method) we'll create a blank for
    	
def quiz1(request):
    a=Question.objects.all()

    if request.method=='POST':
        forms=Userform(request.POST,request.FILES)
        print(request.POST,'___________________')
        if forms.is_valid():
            forms.save()
            z=Question.objects.get(id=int(request.POST['user']) )
            if(z.ans== request.POST['yourans']):
                r="CORRECT"
            else:
                r="INCORRECT"
            return render(request, 'result.html',{'z':z,'forms':forms,'r':r})
    forms=Userform()
    return render(request, 'result.html',{'a':a,'forms':forms})


            

    
    