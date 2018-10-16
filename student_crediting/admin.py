from django.contrib import admin
#from django.shortcuts import redirect
from django.urls import reverse

from .models import ExGroup, Student, Sheet, Exercise, Result, Presence, Config


#print (reverse('students'))

#admin.site.site_url = reverse('students')
#admin.site.site_url = 'https://10.4.73.214:8443/tutorsbase/'# reverse('students')
admin.site.site_url = '../../'# reverse('students')

admin.site.register(ExGroup)
admin.site.register(Student)
admin.site.register(Sheet)
admin.site.register(Exercise)
admin.site.register(Result)
admin.site.register(Presence)
admin.site.register(Config)
