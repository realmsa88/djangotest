from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

class auth_user_details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, null=True)
    birthdate = models.DateField(null=True)

    def __str__(self):
        return f"{self.user} - {self.phone_number} - {self.address} - {self.birthdate}"

class TeachingMode(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Instrument(models.Model):
    instrument_minor_name = models.CharField(max_length=50, null=True)
    instrument_major_name = models.CharField(max_length=50, null=True)
    

    def __str__(self):
        return f"{self.instrument_minor_name} {self.instrument_major_name}"
    

class Teacher (models.Model) :
    teacher = models.ForeignKey(auth_user_details, on_delete=models.CASCADE)
    teachingmode = models.ForeignKey(TeachingMode, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, null=True)

    def __str__ (self) :
        return self.teacher.user.username 

class Book (models.Model) :

    book = models.CharField(max_length=20,null=True)

    def __str__(self) :
        return self.book
    
class BookInstrument(models.Model) :

    bookID = models.ForeignKey(Book, on_delete=models.CASCADE)
    instrumentID = models.ForeignKey(Instrument, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bookID} - {self.instrumentID}"

class ModuleDetails(models.Model) :

    module_type = models.CharField(null=True, max_length=255)
    module_name = models.CharField(null=True, max_length=255)
    description = models.CharField(null=True, max_length=255)
    bookInstrument = models.ForeignKey(BookInstrument, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.module_type} - {self.module_name} - {self.description} - {self.bookInstrument}"

class Activity(models.Model) :

    activity_name = models.CharField(max_length=255, null=True)
    activity_type = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True)
    activity_date = models.DateField(null=True) 
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    def __str__(self) :
        return self.activity_name, self.activity_type, self.description, self.category, self.location, self.activity_date, self.start_time, self.end_time

class Album(models.Model):

    activityID = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return self.activityID
    
class Media(models.Model):
    albumID = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)  
    media_type = models.CharField(max_length=20, null=True)
    media_name = models.ImageField(upload_to='media_files/', null=True, blank=True)

    def __str__(self):
        return str(self.media_name)  # Convert to string


class Student(models.Model):
    studentName = models.CharField(max_length=255)
    birthdate = models.DateField(null=True) 
    identification_number = models.CharField(max_length=255, unique=True, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=255,null=True)
    race = models.CharField(max_length=255, null=True)
    picture = models.ImageField(null=True)
    assigned_teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='student_assigned_teacher')
    assigned_parent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='student_assigned_parent')
    teaching_mode = models.ForeignKey(TeachingMode, on_delete=models.CASCADE, null=True)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.studentName  # Return the student's name

    def clean(self):
        # if self.assigned_teacher.groups.filter(name='teacher').exists():
        #     raise ValidationError('The assigned teacher must be a member of the "teacher" group.')
        pass


class ParentLogin(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent.username} - {self.login_time}"
    

class TeacherLogin(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.username} - {self.login_time}"