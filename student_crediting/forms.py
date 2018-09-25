from django import forms

from .models import Result

class GiveCreditForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    max_values = kwargs.pop('max_values', None)
    super(GiveCreditForm, self).__init__(*args, **kwargs)
    self.fields['credits'] = forms.IntegerField(min_value=0, max_value=max_values['credits'])
    self.fields['bonus_credits'] = forms.IntegerField(min_value=0, max_value=max_values['bonus_credits'])

  class Meta:
    model = Result
    fields = ('student', 'exercise', 'credits', 'bonus_credits', 'blackboard',)

