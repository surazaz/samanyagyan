from django import forms
from QuesAns.models import Question,UserAns


class NameForm(forms.Form):
	
	number=forms.DecimalField(label='Choose question number',max_digits=8, decimal_places=2)
	answer = forms.CharField(label='Your answer', max_length=100)


class Userform(forms.ModelForm):
	class Meta:
		model=UserAns
		fields='__all__'