from django import forms

from .models import Result, Student, Exercise, Presence, Sheet

class GiveCreditForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    max_values = kwargs.pop('max_values', None)
    user = kwargs.pop('user', None)
    super(GiveCreditForm, self).__init__(*args, **kwargs)
    if max_values:
      self.fields['credits'] = forms.DecimalField(min_value=0, max_value=max_values['credits'])
      self.fields['bonus_credits'] = forms.DecimalField(min_value=0, max_value=max_values['bonus_credits'])
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





class EditStudentForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super(EditStudentForm, self).__init__(*args, **kwargs)
#    if 'instance' in kwargs and kwargs['instance']:
#      ## in this case we selected a student and exercise sheet -> fix them in the form
#      _students = Student.objects.filter(id=kwargs['instance'].student.id)
#      _sheet = Sheet.objects.filter(id=kwargs['instance'].sheet.id)
#      self.fields['student'].queryset = _students
#      self.fields['student'].initial = _students
#      self.fields['sheet'].queryset = _sheet
#      self.fields['sheet'].initial = _sheet
#
#    else:
#      if user:
#        _students = Student.objects.select_related('exgroup__tutor').filter(exgroup__tutor=user)
#        self.fields['student'].queryset = _students
#        self.fields['student'].initial = _students

  class Meta:
    model = Student
    fields = ('email', )
