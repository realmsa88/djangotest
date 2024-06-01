from django.contrib.auth.models import User
from django.db import models
from administrator.models import Student, ModuleDetails

# Create your models here.

class ProgressBar(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleDetails, on_delete=models.CASCADE)
    result = models.CharField(null=True, max_length=20)

    def __str__(self):
        return f"{self.student} - {self.module} - {self.result}"

 

