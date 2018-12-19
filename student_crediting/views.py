from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, send_mail

from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import GiveCreditForm, AssignPresenceForm, EditStudentForm, EditStudentFullForm, EditSheetForm
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import pytz

from .models import Student, Exercise, ExGroup, Sheet, Result, Presence, Config

from django.db.models import Avg, Count, Min, Sum, F, Q, StdDev
from django.db.models import FloatField
import numpy as np
import datetime as dt
import time

CURRENT_EVENT = settings.CURRENT_EVENT


def logged_out(request):
  context = {'lecture': CURRENT_EVENT,
             'logged_user': request.user,
             'config': config_read(),
             }
  return render(request, 'registration/my_logged_out.html', context)


@login_required
def redirect_index(request):
  return redirect('students')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('students')
        else:
#            messages.error(request, 'Please correct the error below.')
            pass
    else:
        form = PasswordChangeForm(request.user)
    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }
    return render(request, 'student_crediting/change_password.html', context)


def config_read():
  _conf = Config.objects.all()
  _config = {}
  for _c in _conf:
    _config[_c.name] = _c.state
  return _config


@login_required
def give_credit(request, credit_pk=None):
  _config = config_read()
  if credit_pk:
    instance = get_object_or_404(Result, pk=credit_pk)
    ex_credits = instance.exercise.credits
    ex_bonus_credits = instance.exercise.bonus_credits
    mvs={'credits':ex_credits, 'bonus_credits':ex_bonus_credits}
  else:
    mvs=None
    instance=None
  form = GiveCreditForm(request.POST or None, max_values=mvs, instance=instance, user=request.user, config=_config)
  if form.is_valid():
    student = Student.objects.select_related('exgroup__tutor').get(id=request.POST['student'])
    if student.exgroup.tutor == request.user or request.user.is_staff:
      # only staff and assigned tutor(s) are allowed to edit
      sc = form.save(commit=False)
      sc.edited_by = request.user
      sc.last_modified = timezone.now()
      sc.save()
      send_mail_to_student(request)
      return redirect('student_details', sc.student.id)
    else:
      raise PermissionDenied("Permission denied.")
  else:
    #messages.error(request, 'Please correct the error below.')

    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }
    return render(request, 'student_crediting/give_credits.html', context)


@login_required
def send_mail_to_student(request):
  if settings.SEND_CREDIT_UPDATES_TO_STUDENTS:
    ## check if exercise sheet is fully graded (and presence is assigned) and send mail if so
    if 'exercise' in request.POST:
      exercise = get_object_or_404(Exercise, pk=request.POST['exercise'])
      this_sheet = exercise.sheet
      this_sheetno = exercise.sheet.number
    elif 'sheet' in request.POST:
      this_sheet = get_object_or_404(Sheet, pk=request.POST['sheet'])
      this_sheetno = this_sheet.number
    #total_credits_achieved = Sum('result__credits', filter=Q(result__exercise__sheet__number__lte=this_sheetno))
    total_credits_achieved = Sum('result__credits', filter=(Q(result__exercise__sheet__number__lte=this_sheetno)&(~Q(result__blackboard='-'))))
    num_bbp = Count('result__blackboard', filter=(Q(result__exercise__sheet__number__lte=this_sheetno)&Q(result__blackboard='+')))
    num_bbo = Count('result__blackboard', filter=(Q(result__exercise__sheet__number__lte=this_sheetno)&Q(result__blackboard='o')))
    num_bbm = Count('result__blackboard', filter=(Q(result__exercise__sheet__number__lte=this_sheetno)&Q(result__blackboard='-')))
    student = Student.objects.annotate(num_graded=Count('id', filter=Q(result__exercise__sheet=this_sheet))).annotate(total_credits_achieved=total_credits_achieved).annotate(num_bbp=num_bbp).annotate(num_bbo=num_bbo).annotate(num_bbm=num_bbm).get(pk=request.POST['student'])
    if not student.email:
      print ("ERROR: Student's email missing. Will not send status update.")
      return 1
    credits_sum = Sum('exercise__credits', distinct=True)
    sheet = Sheet.objects.annotate(num_exercises=Count('exercise', distinct=True)).annotate(credits_sum=credits_sum).get(number=this_sheetno)
    credits_possible = Sheet.objects.filter(number__lte=this_sheetno).aggregate(credits_possible=Sum('exercise__credits'))
    eg = Presence.objects.filter(sheet__number__lte=this_sheetno, present=False, student=student).aggregate(tutorials_missed=Count('id'))
    presence = Presence.objects.filter(sheet=sheet, student=student).values_list('present', flat=True)
    presence_assigned = len(presence)==1
    if presence_assigned and (student.num_graded==sheet.num_exercises):
      results = Result.objects.filter(exercise__sheet=sheet, student=student).order_by('exercise__number')
      if presence[0]:
        presence_string = 'ja' 
      else: 
        presence_string = 'nein' 
      subject = 'Ergebnisse Blatt Nr {}'.format(sheet.number)
      body = "Liebe(r) {} {},\n\ndie folgenden Ergebnisse wurden zu Blatt Nr {} im System eingetragen:\n\n".format(student.name, student.surname, sheet.number)
      body += "    Anwesenheit im Tutorat: {}\n".format(presence_string)
      for res in results:
        body += "    Aufgabe {}: {:.1f} Punkt(e)".format(res.exercise.number, res.credits)
        if res.blackboard:
          body += " (Tafel: '{}')".format(res.blackboard)
        body += "\n"
      tutorials_missed = 2
      body += "\nDein aktueller Punktestand ist {:.1f}/{:.0f}. Du hast {} mal im Tutorat gefehlt.\n".format(student.total_credits_achieved, credits_possible['credits_possible'], eg['tutorials_missed'])
      nm = student.num_bbm
      no = student.num_bbo
      np = student.num_bbp
      nbb = nm+no+np
      body += "Du hast {} mal an der Tafel vorgerechnet".format(nbb)
      if nbb:
        body += " ("
        _b = []
        if nm:
          _b.append("'-': {} mal".format(nm))
        if no:
          _b.append("'o': {} mal".format(no))
        if np:
          _b.append("'+': {} mal".format(np))
        body += ', '.join(_b)
        body += ")"
      body += ".\n"


      body += "\nDiese Email wurde automatisch erstellt.\nBitte wende dich bei Unklarheiten an deinen Tutor {} {}.".format(student.exgroup.tutor.first_name, student.exgroup.tutor.last_name)
      body += "\n\nLiebe Grüße\nDein Ex1-Team"
      to = (student.email, )
      bcc = [student.exgroup.tutor.email,]
      for bm in settings.BCC_MAILTO:
        bcc.append(bm)
      email = EmailMessage(subject=subject, body=body, to=to, bcc=bcc)
      email.send()

      if settings.DEBUG_MAIL:
        dbmessage = 40*'^'+'\n' 
        dbmessage += 'To: {}\nFrom: {}\nBcc: {}\nSubject: {}\nBody:\n{}'.format(to, settings.DEFAULT_FROM_EMAIL, bcc, subject, body)
        dbmessage += '\n'+40*'^' 
        send_mail(
            subject='Debug Mail',
            message=dbmessage,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.BCC_MAILTO,],
            fail_silently=True,
        )
      return 0


@login_required
def exercise_sheets(request):
  # 1) find out how many students each exgroup has ## NOT EACH! THE EXGROUP assigned to THIS user!
  # 2) figure out how many exercises each sheet has
  #   2a) compute for each exgroup how many exercises have to be graded
  #   2b) compute for each exgroup how many presences have to be assigned
  # 3) find out for each exgroup AND each each sheet 
  #   3a) how many exercises are graded
  #   3b) how many presences are assigned

  result_sheet = []
  sheets = Sheet.objects.annotate(num_exercises=Count('exercise', distinct=True))
  ## step 1)
  if not request.user.is_staff:
    exgroup = ExGroup.objects.annotate(num_students=Count('student', distinct=True)).get(tutor=request.user)
    #print ("{} {}".format(exgroup,exgroup.num_students))
    nstudents = exgroup.num_students

    ## step 2)
    for sh in sheets:
      #print ("{} has {} exercises".format(sh, sh.num_exercises))
      result_sheet.append({})
      result_sheet[-1]['number'] = sh.number
      result_sheet[-1]['deadline'] = sh.deadline
      result_sheet[-1]['num_exercises'] = sh.num_exercises
      result_sheet[-1]['exercises_to_be_graded'] = sh.num_exercises*nstudents
      result_sheet[-1]['presences_to_be_assigned'] = nstudents
      result_sheet[-1]['link_sheet'] = sh.link_sheet
      result_sheet[-1]['link_solution'] = sh.link_solution

    ## step 3)
    students = Student.objects.filter(exgroup__tutor=request.user)
    #print (students)
    _gc = True
    for sh in result_sheet:
      ## we always want to show the solutions to one exercise sheet in advance compared to what the tutors entered in the database
      sh['show_solutions'] = _gc
      qs_r = Result.objects.values('student').annotate(num_results=Count('id')).filter(exercise__sheet=sh['number']).filter(student__exgroup__tutor=request.user)
      _sum_exgraded = 0
      for qss in qs_r:
        _sum_exgraded += qss['num_results']
      sh['exercises_graded'] = _sum_exgraded
      qs_p = Presence.objects.values('student').annotate(num_present=Count('id')).filter(sheet=sh['number']).filter(student__exgroup__tutor=request.user)
      _sum_passigned = 0
      for qss in qs_p:
        _sum_passigned += qss['num_present']
      sh['presences_assigned'] = _sum_passigned
      print ("Sheet No{}: total_exgraded={}  total_passigned={} (qsr={}; qsp={})".format(sh['number'], _sum_exgraded, _sum_passigned, qs_r, qs_p))
      if request.user.is_staff:
        sh['grading_completed'] = True
        print ("True")
      elif (sh['exercises_to_be_graded']==sh['exercises_graded'] and sh['presences_to_be_assigned']==sh['presences_assigned']):
        sh['grading_completed'] = True
      else:
        sh['grading_completed'] = False
      _gc = sh['grading_completed']  ## remember this value to set 'show_solutions' accordingly in next iteration

  else:
    ## Staff can always see solutions
    for sh in sheets:
      result_sheet.append({})
      result_sheet[-1]['number'] = sh.number
      result_sheet[-1]['deadline'] = sh.deadline
      result_sheet[-1]['show_solutions'] = True
      result_sheet[-1]['link_sheet'] = sh.link_sheet
      result_sheet[-1]['link_solution'] = sh.link_solution



  context = {'sheets': sheets,
             'results': result_sheet,
             'lecture': CURRENT_EVENT,
             'logged_user': request.user,
             'config': config_read(),
             }

  return render(request, 'student_crediting/exercise_sheets.html', context)



@login_required
def students(request):
  #sum_credits = Exercise.objects.all().aggregate(total_credits=Sum('credits'), total_bonus_credits=Sum('bonus_credits'))
  sum_credits = Exercise.objects.filter(sheet__deadline__lt=timezone.now()).aggregate(total_credits=Sum('credits'), total_bonus_credits=Sum('bonus_credits'))
  if request.user.is_staff:
    student_list = Student.objects.all()
  else:
    student_list = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=request.user)
  student_list = student_list.annotate(credits_sum=Sum('result__credits', filter=~Q(result__blackboard='-')), 
                                       bonus_credits_sum=Sum('result__bonus_credits', filter=~Q(result__blackboard='-')),
                                       credits_sum_perc=100*Sum('result__credits', filter=~Q(result__blackboard='-'))/sum_credits['total_credits'],
                                       bonus_credits_sum_perc=100*Sum('result__bonus_credits', filter=~Q(result__blackboard='-'))/sum_credits['total_bonus_credits'],
                                       ).order_by('exgroup__number','surname')
#  student_list = student_list.annotate(credits_sum=Sum('result__credits', filter=~Q(result__blackboard='-')), 
#                                       bonus_credits_sum=Sum('result__bonus_credits', filter=~Q(result__blackboard='-')),
#                                       credits_sum_perc=100*F('credits_sum')/sum_credits['total_credits'],
#                                       bonus_credits_sum_perc=100*F('bonus_credits_sum')/sum_credits['total_bonus_credits'],
#                                       ).order_by('exgroup__number','surname')

  context = {#'form': form,
             'student_list': student_list,
             'lecture': CURRENT_EVENT,
             'logged_user': request.user,
             'config': config_read(),
             }

  return render(request, 'student_crediting/students.html', context)


@login_required
def student_details(request, student_pk):
  student = Student.objects.select_related('exgroup__tutor').get(pk=student_pk)
  exercises = Exercise.objects.select_related('sheet')
  presence = Presence.objects.filter(student=student_pk)
  sheets_meta = {}
  ## step 1: fill sheet and exercises information to dict 'sheets_meta'
  for iex, ex in enumerate(exercises):
    if not ex.sheet.number in sheets_meta:
      sheets_meta[ex.sheet.number] = {}
      _ispres = presence.filter(sheet=ex.sheet.number)
      if _ispres:
        sheets_meta[ex.sheet.number]['presence'] = _ispres[0]
      else:
        sheets_meta[ex.sheet.number]['presence'] = None
    if not ex.number in sheets_meta[ex.sheet.number]:
      sheets_meta[ex.sheet.number][ex.number] = {}
      sheets_meta[ex.sheet.number][ex.number]['exercise_pk'] = ex.id
      sheets_meta[ex.sheet.number][ex.number]['credits'] = ex.credits
      sheets_meta[ex.sheet.number][ex.number]['bonus_credits'] = ex.bonus_credits
      sheets_meta[ex.sheet.number][ex.number]['credit_pk'] = None
      sheets_meta[ex.sheet.number][ex.number]['credits_achieved'] = None
      sheets_meta[ex.sheet.number][ex.number]['bonus_credits_achieved'] = None
      sheets_meta[ex.sheet.number][ex.number]['blackboard_performance'] = None

  ## step2: insert student's achievements into above dict 'sheets_meta'
  student_result = Result.objects.filter(student=student_pk).select_related('exercise__sheet')
  for sr in student_result:
    sheets_meta[sr.exercise.sheet.number][sr.exercise.number]['credits_achieved'] = sr.credits
    sheets_meta[sr.exercise.sheet.number][sr.exercise.number]['bonus_credits_achieved'] = sr.bonus_credits
    sheets_meta[sr.exercise.sheet.number][sr.exercise.number]['credit_pk'] = sr.id
    sheets_meta[sr.exercise.sheet.number][sr.exercise.number]['blackboard_performance'] = sr.blackboard

  ## step3: reorganize dict 'sheets_meta' such that django template can visualize
  rdata = []
  for snumber in sheets_meta:
    rdata.append({})
    rdata[-1]['sheet'] = snumber
    rdata[-1]['presence'] = sheets_meta[snumber]['presence']
    rdata[-1]['sheet_data'] = []
    for exnumber in sorted(sheets_meta[snumber]):
      if exnumber == 'presence':
        continue
      rdata[-1]['sheet_data'].append({})
      rdata[-1]['sheet_data'][-1]['exercise'] = exnumber
      for md in sheets_meta[snumber][exnumber]:
        rdata[-1]['sheet_data'][-1][md] = sheets_meta[snumber][exnumber][md]

  context = {#'form': form,
             'student': student,
             'rdata': rdata,
             'lecture': CURRENT_EVENT,
             'logged_user': request.user,
             'config': config_read(),
             }
  return render(request, 'student_crediting/student_detail.html', context)


@login_required
def exgroup_details(request, exgroup_pk):
  if not request.user.is_staff:
    raise PermissionDenied("Permission denied")
  exgroup = get_object_or_404(ExGroup, id=exgroup_pk)
  context = {
      'exgroup':exgroup,
      'lecture': CURRENT_EVENT,
      'logged_user': request.user,
      'config': config_read(),
      }
  return render(request, 'student_crediting/exgroup_detail.html', context)




@login_required
def edit_credits(request, student_pk, sheet_no, exercise_pk):
  ## generates new Results object with above data and passes the pk of this object to 'give_credit' function
  student = get_object_or_404(Student, id=student_pk)
  if not (student.exgroup.tutor == request.user or request.user.is_staff):
    raise PermissionDenied("Permission denied")
  exercise = get_object_or_404(Exercise, id=exercise_pk)
  try:
    res = Result.objects.filter(student=student, exercise=exercise)[0]
  except:
    res = Result.objects.create(student=student, exercise=exercise, edited_by=request.user, )
  return give_credit(request, credit_pk=res.id)


@login_required
def give_presence(request, student_pk, sheet_no):
  student = get_object_or_404(Student, id=student_pk)
  if not (student.exgroup.tutor == request.user or request.user.is_staff):
    raise PermissionDenied("Permission denied")
  sheet = get_object_or_404(Sheet, number=sheet_no)
  #print ('student: ', student)
  #print ('sheet: ', sheet)
  try:
    pres = Presence.objects.filter(student=student, sheet=sheet)[0]
  except:
    pres = Presence.objects.create(student=student, sheet=sheet)
  return edit_presence(request, presence_pk=pres.id)


@login_required
def edit_presence(request, presence_pk=None):
  if presence_pk:
    instance = get_object_or_404(Presence, pk=presence_pk)
  else:
    instance=None
  form = AssignPresenceForm(request.POST or None, instance=instance, user=request.user)
  if form.is_valid():
    student = Student.objects.select_related('exgroup__tutor').get(id=request.POST['student'])
    if student.exgroup.tutor == request.user or request.user.is_staff:
      # only staff and assigned tutor(s) are allowed to edit
      sc = form.save(commit=False)
      sc.save()
      send_mail_to_student(request)
      return redirect('student_details', sc.student.id)
    else:
      raise PermissionDenied("Permission denied.")
  else:
    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }

    return render(request, 'student_crediting/assign_presence.html', context)

@login_required
def edit_sheet(request, sheet_pk=None):
  if not request.user.is_staff:
    raise PermissionDenied("Permission denied.")
  if sheet_pk:
    sheet = get_object_or_404(Sheet, number=sheet_pk)
  else:
    ## create new sheet
    sheet = None
  form = EditSheetForm(request.POST or None, instance=sheet)
  if form.is_valid():
#    print ("*******************")
#    print("request.POST:", request.POST)
#    print ("*******************")
    if not sheet:
      sheet = Sheet()
      sheet.number = request.POST['number']
    sheet.link_sheet = request.POST['link_sheet']
    sheet.link_solution = request.POST['link_solution']
    naive = parse_datetime("{} {}".format(request.POST['deadline_day'], request.POST['deadline_time']))
    _dl = pytz.timezone("Europe/Berlin").localize(naive, is_dst=None)
    sheet.deadline = _dl
    sheet.save()
    return redirect('exercise_sheets')
  else:
    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }

    return render(request, 'student_crediting/edit_sheet.html', context)

 


@login_required
def edit_student_mail(request, student_pk=None):
  if not student_pk:
    raise PermissionDenied("Permission denied.")
#  current_event = 'Experimental Physics I'
#  current_user = request.user
  instance = get_object_or_404(Student, pk=student_pk)
  form = EditStudentForm(request.POST or None, instance=instance, user=request.user)
  if form.is_valid():
    student = Student.objects.select_related('exgroup__tutor').get(id=student_pk)
    if student.exgroup.tutor == request.user or request.user.is_staff:
      # only staff and assigned tutor(s) are allowed to edit
      sc = form.save(commit=False)
      sc.save()
      return redirect('student_details', student_pk)
    else:
      raise PermissionDenied("Permission denied.")
  else:
    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }

    return render(request, 'student_crediting/edit_student.html', context)


@login_required
def edit_student_full(request, student_pk=None):
  if not student_pk:
    raise PermissionDenied("Permission denied.")
  instance = get_object_or_404(Student, pk=student_pk)
  form = EditStudentFullForm(request.POST or None, instance=instance)
  if form.is_valid():
    student = Student.objects.select_related('exgroup__tutor').get(id=student_pk)
    if request.user.is_staff:
      # only staff and assigned tutor(s) are allowed to edit
      sc = form.save(commit=False)
      sc.save()
      return redirect('student_details', student_pk)
    else:
      raise PermissionDenied("Permission denied.")
  else:
    context = {'form': form,
               'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               }

    return render(request, 'student_crediting/edit_student.html', context)




@login_required
def show_stats(request):
  if not request.user.is_staff:
    raise PermissionDenied("Permission denied.")
  else:
    results = Result.objects.select_related('student__exgroup__tutor').all()
    credit_values = [] # [float(fl) for fl in results.values_list('credits', flat=True)]
    for egroup in ExGroup.objects.select_related('tutor').all():
      credit_values.append({})
      credit_values[-1]['tutor'] = egroup.tutor.last_name
      credit_values[-1]['group'] = egroup.id
      for fl in results.filter(student__exgroup=egroup).values_list('credits', flat=True):
        print (fl)
      try:
        credit_values[-1]['data'] = [float(fl) for fl in results.filter(student__exgroup=egroup).values_list('credits', flat=True)]
      except:
        pass

    context = {'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               'credit_values': credit_values,
               }
    return render(request, 'student_crediting/statistics.html', context)


@login_required
def stats_overview(request):
  if not request.user.is_staff:
    raise PermissionDenied("Permission denied.")
  else:
    consider_students = Student.objects.annotate(credits_sum=Sum('result__credits')).exclude(credits_sum=0)
    #results = Result.objects.select_related('student__exgroup__tutor').all()
    results = Result.objects.select_related('student__exgroup__tutor').filter(student__in=consider_students)
    credit_values = [] # [float(fl) for fl in results.values_list('credits', flat=True)]
    for egroup in ExGroup.objects.select_related('tutor').all().order_by('number'):
      credit_values.append({})
      credit_values[-1]['tutor'] = egroup.tutor.last_name
      credit_values[-1]['group'] = egroup.number

      my_list = list(results.filter(student__exgroup=egroup).values_list('credits', flat=True))
      try:
        # convert values to float and remove np.nan/None values:
        _dat = np.array(my_list, dtype=np.float)
        _dat = _dat[~np.isnan(_dat)]
        credit_values[-1]['data'] = list(_dat)
      except:
        credit_values[-1]['data'] = None

    ## histogram data using numpy:
    for eg in credit_values:
      raw_data = eg['data']
      #if type(raw_data) == np.array:
      if raw_data and len(raw_data)>0:
        #print ('raw_data: ', raw_data)
        _h, _edges = np.histogram(raw_data, bins=11, range=(0,10), density=True)
        eg['hist'] = list(_h)
        eg['edges'] = _edges
        #print ("G{}: data={}, hist={}, edges={}".format(eg['group'],eg['data'],eg['hist'],eg['edges']))

    context = {'lecture': CURRENT_EVENT,
               'logged_user': request.user,
               'config': config_read(),
               'credit_values': credit_values,
               }
    return render(request, 'student_crediting/statistics_overview.html', context)

@login_required
def stats_detail(request):
  if not request.user.is_staff:
    raise PermissionDenied("Permission denied.")
  sheets = Sheet.objects.all().order_by('number')
  shs = []
  for sh in sheets:
    shs.append({})
    shs[-1]['number'] = sh.number
    shs[-1]['exercises'] = Exercise.objects.filter(sheet=sh).order_by('number')
    shs[-1]['deadline'] = sh.deadline
    shs[-1]['exgroups'] = []
    exgroups = ExGroup.objects.exclude(number=10).order_by('number')
    consider_students = Student.objects.annotate( credits_sum=Sum('result__credits', filter=(Q(result__exercise__sheet=sh) & Q(result__credits__isnull=False)) ) ).exclude(credits_sum=0).order_by('pk')
    cs_pk = list(consider_students.values_list('pk' ,flat=True))
#    print ("I consider the following students for sheet No{}:".format(sh.number))
#    for _is in consider_students:
#      print ("\t(id{}) {} {}: {:.2f}".format(_is.pk, _is.name, _is.surname, _is.credits_sum))
    for eg in exgroups:
      avg = Avg('result__credits', output_field=FloatField(), filter=( Q(result__student__exgroup=eg) & Q(result__exercise__sheet=sh) & Q(result__credits__isnull=False) & Q(result__student__pk__in=cs_pk) ))
      stddev = StdDev('result__credits', sample=False, output_field=FloatField(), filter=( Q(result__student__exgroup=eg) & Q(result__exercise__sheet=sh) & Q(result__credits__isnull=False)  & Q(result__student__pk__in=cs_pk) ))
      csum = Sum('result__credits', output_field=FloatField(), filter=( Q(result__student__exgroup=eg) & Q(result__exercise__sheet=sh) & Q(result__credits__isnull=False)  & Q(result__student__pk__in=cs_pk) ))
      errp = F('avg')+F('stddev')
      errn = F('avg')-F('stddev')
      avgp = F('avg')+0.15
      avgn = F('avg')-0.15
      ex = Exercise.objects.annotate(avg=avg).annotate(csum=csum).annotate(stddev=stddev).annotate(errp=errp).annotate(errn=errn).annotate(avgp=avgp).annotate(avgn=avgn).filter(sheet=sh).order_by('number')
      #ex = Exercise.objects.annotate(avg=avg).annotate(avgp=avgp).annotate(avgn=avgn).filter(sheet=sh).order_by('number')
      shs[-1]['exgroups'].append({})
      shs[-1]['exgroups'][-1]['number']=eg.number
      shs[-1]['exgroups'][-1]['tutor']=eg.tutor.last_name
      shs[-1]['exgroups'][-1]['exercises']=ex
      _low, _high, _avg = 0,0,0
      totavg = Avg('credits', filter=( Q(student__exgroup=eg) & Q(exercise__sheet=sh.number)  & Q(credits__isnull=False)  & Q(student__pk__in=cs_pk)) )
      _ta = Result.objects.aggregate(totavg=totavg)
      _ta = _ta['totavg']
      totstd = StdDev('credits', sample=False, filter=( Q(student__exgroup=eg) & Q(exercise__sheet=sh.number)  & Q(credits__isnull=False)  & Q(student__pk__in=cs_pk)) )
      _ts = Result.objects.aggregate(totstd=totstd)
      _ts = _ts['totstd']
      if _ta and _ts:
        _low = _ta - _ts
        _high = _ta + _ts
        _avg = _ta

      shs[-1]['exgroups'][-1]['total']={'low':_low, 'high':_high, 'avg':_avg}

  context = {'lecture': CURRENT_EVENT,
             'logged_user': request.user,
             'config': config_read(),
             'rsheets': shs,
             'sheets': sheets,
             }
  return render(request, 'student_crediting/statistics_detail.html', context)

 
