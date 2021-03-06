from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from django.conf import settings

from . import views
from student_crediting import views as student_crediting_views


#extra_context = {'lecture': 'Experimental Physics I', 'logged_user': 'not logged in' }
#extra_context = {'logged_user': 'Experimental Physics I', }
#extra_context = {'lecture': 'Experimental Physics I', }
extra_context = {'lecture': settings.CURRENT_EVENT, }




urlpatterns = [
#    url(r'^$', student_crediting_views.redirect_index, name='index'),
    url(r'^$', views.students, name='students'),
    url(r'^student/(?P<student_pk>[0-9]+)/$', views.student_details, name='student_details'),
    url(r'^student/([0-9]+)/(?P<credit_pk>[0-9]+)$', views.give_credit, name='edit_credits'),
    url(r'^student/(?P<student_pk>[0-9]+)/credits/new/(?P<sheet_no>[0-9]+)/(?P<exercise_pk>[0-9]+)$', views.edit_credits, name='give_credits'),
    url(r'^student/(?P<student_pk>[0-9]+)/presence/new/(?P<sheet_no>[0-9]+)$', views.give_presence, name='give_presence'),

    path('student/<int:student_pk>/examcredits/<int:credit_pk>', views.give_examcredits, name='edit_examcredits'),
    path('student/<int:student_pk>/examcredits/new/<int:exam_pk>/<int:exercise_pk>', views.edit_examcredits, name='give_examcredits'),
    path('student/<int:student_pk>/exampresence/new/<int:exam_pk>', views.give_exampresence, name='give_exampresence'),
    path('student/<int:student_pk>/exampresence/update/<int:presence_pk>', views.edit_exampresence, name='edit_exampresence'),

    url(r'^student/([0-9]+)/presence/update/(?P<presence_pk>[0-9]+)$', views.edit_presence, name='edit_presence'),
    url(r'^student/(?P<student_pk>[0-9]+)/edit_mail$', views.edit_student_mail, name='edit_student_mail'),
    url(r'^student/(?P<student_pk>[0-9]+)/edit_student$', views.edit_student_full, name='edit_student_full'),
#    url(r'^stats/$', views.show_stats, name='show_stats'),
    url(r'^stats_overview/$', views.stats_overview, name='stats_overview'),
    url(r'^stats_detail/$', views.stats_detail, name='stats_detail'),
#
    path('stats_exam_overview', views.stats_exam_overview, name='stats_exam_overview'),
#
    url(r'^exercises/sheets$', views.exercise_sheets, name='exercise_sheets'),
    path('exercises/sheets/<int:sheet_pk>/', views.edit_sheet, name='edit_sheet'),
    path('exercises/sheets/new/', views.edit_sheet, name='new_sheet'),
#
    path('exgroup/<int:exgroup_pk>/', views.exgroup_details, name='exgroup_details'),
#
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'extra_context': extra_context}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/my_logged_out.html', 'extra_context': extra_context} , name='logout'),
    url(r'^logged_out/$', student_crediting_views.logged_out, name='logged_out'),
    url(r'^password_change/$', views.change_password, name='change_password'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_myform.html', 'email_template_name':'registration/password_reset_myemail.html', 'subject_template_name':'registration/password_reset_mysubject.txt', 'extra_context': extra_context}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_mydone.html', 'extra_context': extra_context}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_myconfirm.html', 'extra_context': extra_context}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_mycomplete.html', 'extra_context': extra_context}, name='password_reset_complete'),
    ]

#    url(r'^$', student_crediting_views.redirect_index, name='index'),



