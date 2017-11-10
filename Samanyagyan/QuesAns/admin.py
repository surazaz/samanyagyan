from django.contrib import admin
from .models import Question,UserAns
# Register your models here.
#(class name)
admin.site.register(Question)

admin.site.register(UserAns)