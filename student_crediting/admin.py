from django.contrib import admin

from .models import ExGroup, Student, Sheet, Exercise, Result, Presence

admin.site.register(ExGroup)
admin.site.register(Student)
admin.site.register(Sheet)
admin.site.register(Exercise)
admin.site.register(Result)
admin.site.register(Presence)
