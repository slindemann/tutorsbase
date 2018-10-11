from django.db import models
from django.utils import timezone


class Config(models.Model):
  name = models.CharField(max_length=15, help_text="name of config parameter", unique=True)
  state = models.IntegerField(help_text='state of config parameter')
  description = models.CharField(max_length=127, help_text='description of config parameter and its states')

  def __str__(self):
    #return "(ID{}) {}: {} ({}) ".format(self.pk, self.name, self.state, self.description)
    return "[ID{} {}: {} ({})] ".format(self.pk, self.name, self.state, self.description)


class ExGroup(models.Model):
    ## this class holds the data to the exercise groups
    number = models.IntegerField(help_text="Exercise Group No", unique=True)
    tutor = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    venue = models.CharField(default="", max_length=127, help_text="Venue time and place")

    def __str__(self):
       #return "(ID{}) Exercise Group No{}, {} , {}".format(self.pk, self.number, self.tutor, self.venue)
       return "[ID{} Exercise Group No{}, {} , {}]".format(self.pk, self.number, self.tutor, self.venue)



class Student(models.Model):
    ## this class is supposed to hold the metadata to the individual students
    name = models.CharField(max_length=127)
    surname = models.CharField(max_length=127)
    studentID = models.IntegerField(help_text="Student ID", default=None, unique=True)
    exgroup = models.ForeignKey(ExGroup, on_delete=models.PROTECT)
    email = models.EmailField(default=None, blank=True, null=True )

    def __str__(self):
        #return "(ID{}) {} {} ({})".format(self.pk, self.name, self.surname, self.studentID)
        return "[ID{} {} {} ({}; {})]".format(self.pk, self.name, self.surname, self.studentID, self.email)

class Sheet(models.Model):
    ## this class holds the metadata to the exercise sheets
    number = models.IntegerField(help_text="Exercise Sheet No", unique=True)
    deadline = models.DateTimeField(help_text="Due date of exercise")

    def __str__(self):
        return "[ID{} Exercise Sheet No{}]".format(self.pk, self.number)
        #return "(ID{}) Exercise Sheet No{}".format(self.pk, self.number)


class Exercise(models.Model):
    ## this class holds the metadata to the individual (sub-)exercises
    #
    ## do we really want to have the number of the exercise sheet also in the name as suggested below? 
    ## Or take that information from sheet_id?
    number = models.CharField(max_length=127, help_text="e.g., '2c'") # exercise number, e.g., '2c'
    sheet = models.ForeignKey(Sheet, on_delete=models.PROTECT)
    credits = models.DecimalField(default=0, max_digits=4, decimal_places=1, help_text='number of credits') # number of credits to be achieved (excluding bonus credits)
    bonus_credits = models.DecimalField(default=0, max_digits=4, decimal_places=1, help_text='number of bonus credits') # number of bonus credits

    def __str__(self):
      return "[ID{} Ex {} (Sheet {}): [{}+{}] Credits]".format(self.pk, self.number, self.sheet.number, self.credits, self.bonus_credits)
      #return "(ID{}) Ex {} (Sheet {}): [{}+{}] Credits".format(self.pk, self.number, self.sheet.number, self.credits, self.bonus_credits)

    class Meta:
      unique_together = ('number', 'sheet',)


class Result(models.Model):
    ## this class holds the student's results for each individual exercise
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    credits = models.DecimalField(default=None, max_digits=4, decimal_places=1, blank=True, null=True) # number of credits achieved by student in this (sub-)exercise
    bonus_credits = models.DecimalField(default=None, max_digits=4, decimal_places=1, blank=True, null=True) # number of achieved bonus credits by student in this (sub-)exercise
    edited_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    last_modified = models.DateTimeField('date last modified')

    GOOD = '+'
    BAD = '-'
    AVERAGE = 'o'
    NONE = ''
    BLACKBOARD_PERFORMANCE_CHOICES = (
        (GOOD, '+'),
        (AVERAGE, 'o'),
        (BAD, '-'),
			  (NONE, ''),
    )
    blackboard = models.CharField(
        max_length=1,
        choices=BLACKBOARD_PERFORMANCE_CHOICES,
        default=NONE,
				null=True,
        blank=True,
    )

    def __str__(self):
      if self.blackboard:
        #return "[ID{} {} ; {} :  {}+{} credits ({})".format(self.pk, self.exercise, self.student, self.credits, self.bonus_credits, self.blackboard)
        return "[ID{} {} ; {} :  {}+{} credits ({})]".format(self.pk, self.exercise, self.student, self.credits, self.bonus_credits, self.blackboard)
      else:
        #return "(ID{}) {} ; {} :  {}+{} credits".format(self.pk, self.exercise, self.student, self.credits, self.bonus_credits)
        return "[ID{} {} ; {} :  {}+{} credits]".format(self.pk, self.exercise, self.student, self.credits, self.bonus_credits)
    
    class Meta:
      unique_together = ('student', 'exercise',)

    def save(self, *args, **kwargs):
      self.last_modified = timezone.now()
      print ("Result.save: ", self.student, self.exercise, self.credits, self.bonus_credits, self.edited_by, self.last_modified, self.blackboard)
      super(Result, self).save(*args, **kwargs)


class Presence(models.Model):
    # this class holds the presents of the students during the time the exercise sheet was discussed
    sheet = models.ForeignKey(Sheet, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    present = models.BooleanField(default=False)

    def __str__(self):
        return "(ID{}) {} ; {} ; attendance={}".format(self.pk, self.sheet, self.student, self.present)

    class Meta:
      unique_together = ('student', 'sheet',)

