from django.contrib.auth.models import User
from django.db import models
from administrator.models import Student, ModuleDetails, Teacher

# Create your models here.

class ProgressBar(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleDetails, on_delete=models.CASCADE)
    result = models.CharField(null=True, max_length=20)

    def __str__(self):
        return f"{self.student} - {self.module} - {self.result}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    teacher_email = models.ForeignKey(User, on_delete=models.CASCADE,)
    title = models.CharField(null=True, max_length=255)
    absence_reason = models.CharField(null=True, max_length=255)
    description = models.CharField(null=True, max_length=255)
    attendance = models.CharField(null=True, max_length=20)
    date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    status = models.CharField(null=True, max_length=20)
    recurring_weeks = models.IntegerField(default=0) 

    def __str__(self):
        return f"{self.student} - {self.attendance} - {self.title} - {self.date} - {self.start_time} - {self.end_time} - {self.status} - {self.description} - {self.teacher_email} - {self.recurring_weeks}"


 

