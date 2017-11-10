from django.db import models

# Create your models here.
class Question(models.Model):
	ques= models.CharField(max_length=500)
	ans = models.CharField(max_length=255)
	

	def __str__(self):
		return self.ques

class UserAns(models.Model):
	user=models.ForeignKey(Question,on_delete=models.CASCADE)
	yourans=models.CharField(max_length=255)
	def __str__(self):
		return self.yourans

