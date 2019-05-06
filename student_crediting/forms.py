from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget

from django.conf import settings

from .models import Result, Student, Exercise, Presence, Sheet, Exam, ExamExercise, ExamPresence, ExamResult
from django.utils import timezone

class GiveCreditForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    max_values = kwargs.pop('max_values', None)
    user = kwargs.pop('user', None)
    #config = kwargs.pop('config', None)
    super(GiveCreditForm, self).__init__(*args, **kwargs)
    if max_values:
      self.fields['credits'] = forms.DecimalField(min_value=0, max_value=max_values['credits'])
      self.fields['credits'].help_text = 'max. {} credits'.format(max_values['credits'])
      #if not config['bonus_credits']:
      if not settings.BONUS_CREDITS:
        ## if we do not want to use bonus_credits, hide this input 
        self.fields['bonus_credits'].widget = forms.HiddenInput()
      else:
        self.fields['bonus_credits'] = forms.DecimalField(min_value=0, max_value=max_values['bonus_credits'])
        self.fields['bonus_credits'].help_text = 'max. {} bonus_credits'.format(max_values['bonus_credits'])
    if 'instance' in kwargs and kwargs['instance']:
      ## in this case we have selected a student and an exercise before, so fix both:
      _students = Student.objects.filter(id=kwargs['instance'].student.id)
      _exercise = Exercise.objects.filter(id=kwargs['instance'].exercise.id)
      self.fields['student'].queryset = _students
      self.fields['student'].initial = _students
      self.fields['exercise'].queryset = _exercise
      self.fields['exercise'].initial = _exercise
    else:
      if user:
        _students = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=user)
        self.fields['student'].queryset = _students
        self.fields['student'].initial = _students


  class Meta:
    model = Result
    fields = ('student', 'exercise', 'credits', 'bonus_credits', 'blackboard', )


class GiveExamCreditForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    max_values = kwargs.pop('max_values', None)
    user = kwargs.pop('user', None)
    #config = kwargs.pop('config', None)
    super(GiveExamCreditForm, self).__init__(*args, **kwargs)
    if max_values:
      self.fields['credits'] = forms.DecimalField(min_value=0, max_value=max_values['credits'])
      self.fields['credits'].help_text = 'max. {} credits'.format(max_values['credits'])
      #if not config['bonus_credits']:
      if not settings.BONUS_CREDITS:
        ## if we do not want to use bonus_credits, hide this input 
        self.fields['bonus_credits'].widget = forms.HiddenInput()
      else:
        self.fields['bonus_credits'] = forms.DecimalField(min_value=0, max_value=max_values['bonus_credits'])
        self.fields['bonus_credits'].help_text = 'max. {} bonus_credits'.format(max_values['bonus_credits'])
    if 'instance' in kwargs and kwargs['instance']:
      ## in this case we have selected a student and an exercise before, so fix both:
      _students = Student.objects.filter(id=kwargs['instance'].student.id)
      _examexercise = ExamExercise.objects.filter(id=kwargs['instance'].examexercise.id)
      self.fields['student'].queryset = _students
      self.fields['student'].initial = _students
      self.fields['examexercise'].queryset = _examexercise
      self.fields['examexercise'].initial = _examexercise
    else:
      if user:
        _students = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=user)
        self.fields['student'].queryset = _students
        self.fields['student'].initial = _students


  class Meta:
    model = ExamResult
    fields = ('student', 'examexercise', 'credits', 'bonus_credits', )


class AssignPresenceForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(AssignPresenceForm, self).__init__(*args, **kwargs)
    if 'instance' in kwargs and kwargs['instance']:
      ## in this case we selected a student and exercise sheet -> fix them in the form
      _students = Student.objects.filter(id=kwargs['instance'].student.id)
      _sheet = Sheet.objects.filter(id=kwargs['instance'].sheet.id)
      self.fields['student'].queryset = _students
      self.fields['student'].initial = _students
      self.fields['sheet'].queryset = _sheet
      self.fields['sheet'].initial = _sheet

    else:
      if user:
        _students = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=user)
        self.fields['student'].queryset = _students
        self.fields['student'].initial = _students

  class Meta:
    model = Presence
    fields = ('student', 'sheet', 'present')


class AssignExamPresenceForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(AssignExamPresenceForm, self).__init__(*args, **kwargs)
    if 'instance' in kwargs and kwargs['instance']:
      ## in this case we selected a student and exercise sheet -> fix them in the form
      _students = Student.objects.filter(id=kwargs['instance'].student.id)
      _exam = Exam.objects.filter(id=kwargs['instance'].exam.id)
      self.fields['student'].queryset = _students
      self.fields['student'].initial = _students
      self.fields['exam'].queryset = _exam
      self.fields['exam'].initial = _exam

    else:
      if user:
        _students = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=user)
        self.fields['student'].queryset = _students
        self.fields['student'].initial = _students

  class Meta:
    model = ExamPresence
    fields = ('student', 'exam', 'present')


class EditStudentForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(EditStudentForm, self).__init__(*args, **kwargs)

  class Meta:
    model = Student
    fields = ('email', )


class EditStudentFullForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(EditStudentFullForm, self).__init__(*args, **kwargs)

  class Meta:
    model = Student
    fields = ('name', 'surname', 'exgroup', 'studentID', 'matrikelnr' ,'email', )





class DateInput(forms.DateInput):
   input_type = 'date'
# 
# class DateTimeInput(forms.DateTimeInput):
#   input_type = 'datetime'



#import django.contrib.admin.widgets.AdminSplitDateTime
#class CustomAdminSplitDateTime(AdminSplitDateTime):
#  def __init__(self, attrs=None):
#      widgets = [AdminDateWidget, AdminTimeWidget(attrs=None, format='%I:%M %p')]
#      forms.MultiWidget.__init__(self, widgets, attrs)


class EditSheetForm_old(forms.ModelForm):

  class Meta:
    model = Sheet
    fields = ('number', 'deadline', 'link_sheet', 'link_solution' )
    widgets = {
      #'deadline': CustomAdminSplitDateTime(),
      #'deadline': forms.DateInput(attrs={'class': 'datetime-input'}),
      #'deadline': forms.DateInput(attrs={'id': 'datetimepicker1'}),
      'deadline': AdminDateWidget(),
    }



class EditSheetForm(forms.Form):
  number = forms.IntegerField(min_value=1, max_value = 200, required=True, label="Sheet No")
  deadline_day = forms.DateField(required=True, label="Date", widget=DateInput())
  deadline_time = forms.TimeField(required=True, label="Time")
  link_sheet = forms.CharField(required=False, label='Link to Sheet')
  link_solution = forms.CharField(required=False, label='Link to Solution')
  create_exercises = forms.BooleanField(required=False, help_text="Automatically create {} Exercises, {} credits each".format(settings.DEF_NUM_EXERCISES, settings.DEF_NUM_CREDITS))

  def __init__(self, *args, **kwargs):
    self.instance = kwargs.pop('instance', None)
    super(EditSheetForm, self).__init__(*args, **kwargs)

    if self.instance:
      ## in this case we selected a student and exercise sheet -> fix them in the form
      _sheet = self.instance
      self.fields['number'].initial = _sheet.number
      self.fields['number'].disabled = True
      self.fields['deadline_day'].initial = _sheet.deadline
      self.fields['deadline_time'].initial = timezone.localtime(_sheet.deadline) # important to show localtime in field!
      self.fields['link_sheet'].initial = _sheet.link_sheet
      self.fields['link_solution'].initial = _sheet.link_solution
      self.fields['create_exercises'].initial = False
      self.fields['create_exercises'].disabled = True
      self.fields['create_exercises'].widget = forms.HiddenInput()
    else:
      self.fields['deadline_time'].initial = '10:15:00'
      try:
        self.fields['number'].initial = list(Sheet.objects.all().order_by('number').values_list('number', flat=True))[-1]+1
      except IndexError:
        self.fields['number'].initial = 1
      self.fields['number'].disabled = False
      self.fields['deadline_day'].initial = timezone.localtime()
      self.fields['link_sheet'].initial = ''
      self.fields['link_solution'].initial = ''
      self.fields['create_exercises'].initial = False
      self.fields['create_exercises'].disabled = False


