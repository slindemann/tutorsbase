from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from .forms import GiveCreditForm, AssignPresenceForm 
from django.utils import timezone

from .models import Student, Exercise, ExGroup, Sheet, Result, Presence

from django.db.models import Avg, Count, Min, Sum

def logged_out(request):
  context = {}
  return render(request, 'registration/my_logged_out.html', context)


@login_required
def redirect_index(request):
  return HttpResponseRedirect('student_crediting')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'student_crediting/change_password.html', {
        'form': form
    })

@login_required
def give_credit(request, credit_pk=None):
  current_event = 'Experimental Physics I'
  current_user = request.user
  if credit_pk:
    instance = get_object_or_404(Result, pk=credit_pk)
    ex_credits = instance.exercise.credits
    ex_bonus_credits = instance.exercise.bonus_credits
    mvs={'credits':ex_credits, 'bonus_credits':ex_bonus_credits}
  else:
    mvs=None
    instance=None
#  form = GiveCreditForm(request.POST or None, max_values=mvs, instance=instance)
  form = GiveCreditForm(request.POST or None, max_values=mvs, instance=instance, user=request.user)
  if form.is_valid():
    sc = form.save(commit=False)
    sc.edited_by = request.user
    sc.last_modified = timezone.now()
    sc.save()
    return redirect('student_details', sc.student.id)
  else:
    messages.error(request, 'Please correct the error below.')
    context = {'form': form,
               'lecture': current_event,
               'logged_user': current_user,
               }
    return render(request, 'student_crediting/give_credits.html', context)


@login_required
def students(request):
  current_event = 'Experimental Physics I'
  current_user = request.user
  sum_credits = Exercise.objects.all().aggregate(total_credits=Sum('credits'), total_bonus_credits=Sum('bonus_credits'))
  if request.user.is_staff:
    student_list = Student.objects.all()
  else:
    student_list = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=request.user)
  student_list = student_list.annotate(credits_sum=Sum('result__credits'), 
                                          bonus_credits_sum=Sum('result__bonus_credits'), 
                                          credits_sum_perc=100*Sum('result__credits')/sum_credits['total_credits'],
                                          bonus_credits_sum_perc=100*Sum('result__bonus_credits')/sum_credits['total_bonus_credits'],
                                          )
  #print (student_list)
  context = {'lecture': current_event,
             'logged_user': current_user,
             'student_list': student_list.order_by('name'),
             }
  return render(request, 'student_crediting/students.html', context)


@login_required
def student_details(request, student_pk):
  current_event = 'Experimental Physics I'
  current_user = request.user
  student = get_object_or_404(Student, pk=student_pk)
  #exercises = Exercise.objects.select_related('sheet')
  exercises = Exercise.objects.select_related('sheet')
  presence = Presence.objects.filter(student=student_pk)
  #Player.objects.filter(name="Bob").prefetch_related(
  #      'position__positionstats_set', 'playerstats_set')
  sheets_meta = {}
  ## step 1: fill sheet and exercises information to dict 'sheets_meta'
  for iex, ex in enumerate(exercises):
    if not ex.sheet.number in sheets_meta:
      sheets_meta[ex.sheet.number] = {}
      #sheets_meta[ex.sheet.number]['presence'] = 'true'
      #_ispres = presence.filter(sheet=ex.sheet.number).values_list('present', flat=True)
      _ispres = presence.filter(sheet=ex.sheet.number)
      #_ispres = presence.filter(sheet=ex.sheet.number).get('present')
      #print ('presence: ', presence, ', ispres: ', _ispres)
      #print ('ispres: ', _ispres[0])
      if _ispres:
        #sheets_meta[ex.sheet.number]['presence'] = _ispres[0]
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
    for exnumber in sheets_meta[snumber]:
      #print ('exnumber: ', exnumber)
      if exnumber == 'presence':
        continue
      #print ('exnumber: ', exnumber)
      rdata[-1]['sheet_data'].append({})
      rdata[-1]['sheet_data'][-1]['exercise'] = exnumber
      for md in sheets_meta[snumber][exnumber]:
        rdata[-1]['sheet_data'][-1][md] = sheets_meta[snumber][exnumber][md]

  context = {'lecture': current_event,
             'logged_user': current_user,
             'student': student,
             'rdata': rdata,
             }
  return render(request, 'student_crediting/student_detail.html', context)


@login_required
def edit_credits(request, student_pk, sheet_no, exercise_pk):
  ## generates new Results object with above data and passes the pk of this object to 'give_credit' function
  student = get_object_or_404(Student, id=student_pk)
  exercise = get_object_or_404(Exercise, id=exercise_pk)
  try:
    res = Result.objects.filter(student=student, exercise=exercise)[0]
  except:
    res = Result.objects.create(student=student, exercise=exercise, edited_by=request.user, )
  return give_credit(request, credit_pk=res.id)


@login_required
def give_presence(request, student_pk, sheet_no):
  student = get_object_or_404(Student, id=student_pk)
  sheet = get_object_or_404(Sheet, number=sheet_no)
  print ('student: ', student)
  print ('sheet: ', sheet)
  try:
    pres = Presence.objects.filter(student=student, sheet=sheet)[0]
  except:
    pres = Presence.objects.create(student=student, sheet=sheet)
  return edit_presence(request, presence_pk=pres.id)


@login_required
def edit_presence(request, presence_pk=None):
  current_event = 'Experimental Physics I'
  current_user = request.user
  if presence_pk:
    instance = get_object_or_404(Presence, pk=presence_pk)
#    ex_credits = instance.exercise.credits
#    ex_bonus_credits = instance.exercise.bonus_credits
#    mvs={'credits':ex_credits, 'bonus_credits':ex_bonus_credits}
  else:
#    mvs=None
    instance=None
  form = AssignPresenceForm(request.POST or None, instance=instance, user=request.user)
  if form.is_valid():
    sc = form.save(commit=False)
#    sc.edited_by = request.user
#    sc.last_modified = timezone.now()
    sc.save()
    return redirect('student_details', sc.student.id)
  else:
    messages.error(request, 'Please correct the error below.')
    context = {'form': form,
               'lecture': current_event,
               'logged_user': current_user,
               }
    return render(request, 'student_crediting/assign_presence.html', context)


