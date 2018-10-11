from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.students, name='students'),
    url(r'^credits/new$', views.give_credit, name='give_credit'),
    url(r'^student/(?P<student_pk>[0-9]+)/$', views.student_details, name='student_details'),
    url(r'^student/([0-9]+)/(?P<credit_pk>[0-9]+)$', views.give_credit, name='edit_credits'),
    url(r'^student/(?P<student_pk>[0-9]+)/credits/new/(?P<sheet_no>[0-9]+)/(?P<exercise_pk>[0-9]+)$', views.edit_credits, name='edit_credits'),
    url(r'^student/(?P<student_pk>[0-9]+)/presence/new/(?P<sheet_no>[0-9]+)$', views.give_presence, name='give_presence'),
    url(r'^student/([0-9]+)/presence/update/(?P<presence_pk>[0-9]+)$', views.edit_presence, name='edit_presence'),
    url(r'^stats/$', views.show_stats, name='show_stats'),
    ]
