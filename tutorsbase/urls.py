"""tutorsbase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from student_crediting import views
from django.contrib.auth import views as auth_views

from student_crediting import views as student_crediting_views


urlpatterns = [
    url(r'^$', student_crediting_views.redirect_index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'extra_context': {'lecture': 'Experimental Physics I', 'logged_user': 'not logged in' }}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/my_logged_out.html'} , name='logout'),
#    url(r'^logout/$', auth_views.logout, {'next_page': '/logged_out'} , name='logout'),
    url(r'^logged_out/$', student_crediting_views.logged_out, name='logged_out'),
    url(r'^password_change/$', views.change_password, name='change_password'),
    url(r'^student_crediting/', include('student_crediting.urls')),
#
#    url('^', include('django.contrib.auth.urls')),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_myform.html', 'email_template_name':'registration/password_reset_myemail.html', 'subject_template_name':'registration/password_reset_mysubject.txt'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_mydone.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_myconfirm.html'}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_mycomplete.html'}, name='password_reset_complete'),


]
