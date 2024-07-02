from django.forms import ModelChoiceField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
import datetime
from django import forms
from django.core.exceptions import ValidationError
from .models import auth_user_details, Teacher, Student, Instrument,  ModuleDetails, Activity, Book, Billing  # Import your model


class GroupModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class CreateUserForm(UserCreationForm):
    
    group = GroupModelChoiceField(queryset=Group.objects.all(), required=True)

    additional_info = forms.CharField(max_length=100, required=False,
                                      widget=forms.TextInput(attrs={'placeholder': 'Additional Info',
                                                                    'style': 'width: 300px;height:40px;'}))

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Select a group"
        self.fields['username'].widget.attrs['placeholder'] = 'Enter username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter user email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter user first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter user last name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter user password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm user password'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'style': 'width: 300px; height:40px'})  # Set style for all fields

            self.fields['additional_info'].widget.attrs.update()  # Hide additional_info field initially

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get("group")
        if group and group.name == "teacher":
            self.fields['additional_info'].widget.attrs.update({'style': 'width: 300px;height:40px;display:block'})  # Show additional_info field
        else:
            self.fields['additional_info'].widget.attrs.update({'style': 'display:none'})  # Hide additional_info field


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group']

# administrator/forms.py

class UserDetailsForm(forms.ModelForm):
    COUNTRY_CODES = [
        ('+60', 'MY +60'),  # Example country code and label
        ('+1', 'US +1'),    # Example country code and label
        # Add more country codes and labels as needed
    ]

    country_code = forms.ChoiceField(choices=COUNTRY_CODES, required=False)
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter user phone number', 'style': 'width: 180px;height:40px; '}))
    address = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'placeholder': 'Enter user address', 'style': 'width: 300px;height:40px'}))
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'style': 'width: 110px; height: 40px; margin-left: 10px;'
        })
    )
    books = forms.CharField(max_length=100, required=False)
    

    class Meta:
        model = auth_user_details
        fields = ['phone_number', 'address', 'country_code', 'birthdate', 'books']

class TeacherInstrumentForm(forms.Form):
    instruments = forms.ModelMultipleChoiceField(
        queryset=Instrument.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta : 
        model= Teacher
        fields = ['instruments']

class ParentChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = User.objects.filter(groups__name='parent')
        self.empty_label = "Select parent"


class StudentDetailsForm(forms.ModelForm):
    parent_group_id = 3
    teacher_group_id = 2

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    RACE = [
        ('Malay', 'Malay'),
        ('Chinese', 'Chinese'),
        ('Indian', 'Indian'),
        ('Others', 'Others'),
    ]

    # learning_modes = TeachingMode.objects.all()
    # learning_mode_choices = [(mode.id, mode.name) for mode in learning_modes]

    assigned_parent = forms.ModelChoiceField(queryset=User.objects.filter(groups__id=parent_group_id),
                                             empty_label="Select Parent Account")
    assigned_teacher = forms.ModelChoiceField(queryset=User.objects.filter(groups__id=teacher_group_id),
                                              empty_label="Select Assigned Teacher")
    instrument = forms.ModelChoiceField(queryset=Instrument.objects.all(), empty_label="Select Instrument")

    # learningmode = forms.ChoiceField(
    #     choices=learning_mode_choices,
    #     widget=forms.RadioSelect(attrs={'class': 'radio-inline'}),
    #     required=False
    # )

    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    race = forms.ChoiceField(choices=RACE, required=True)
    book = forms.ModelChoiceField(queryset=Book.objects.none(), empty_label="Select Book")
    picture = forms.ImageField(required=False)

    class Meta:
        model = Student
        fields = ['studentName', 'age', 'identification_number', 'birthdate', 'assigned_parent', 'gender', 'race',
                  'assigned_teacher', 'instrument',  'book', 'picture']

    def __init__(self, *args, **kwargs):
        super(StudentDetailsForm, self).__init__(*args, **kwargs)

        parent_group = Group.objects.get(name='parent')
        parent_users = parent_group.user_set.all()

        teacher_group = Group.objects.get(name='teacher')
        teacher_users = teacher_group.user_set.all()
        if 'instrument' in self.data:
            try:
                instrument_id = int(self.data.get('instrument'))
                self.fields['book'].queryset = Book.objects.filter(bookinstrument__instrumentID=instrument_id)
            except (ValueError, TypeError):
                self.fields['book'].queryset = Book.objects.none()
        elif self.instance.pk:
            self.fields['book'].queryset = self.instance.instrument.book_set.order_by('name')
        else:
            self.fields['book'].queryset = Book.objects.none()

        self.fields['assigned_parent'].queryset = parent_users
        self.fields['assigned_parent'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['assigned_parent'].widget.attrs['style'] = 'width: 300px; height: 40px;'

        self.fields['assigned_teacher'].queryset = teacher_users
        self.fields['assigned_teacher'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['assigned_teacher'].widget.attrs['style'] = 'width: 300px; height: 40px;'

        self.fields['instrument'].widget.attrs['style'] = 'width: 300px; height: 40px;'
        self.fields['instrument'].widget.attrs['onchange'] = 'updateBooks()'

        self.fields['gender'].widget.attrs['style'] = 'width: 100px; height: 40px;'
        self.fields['race'].widget.attrs['style'] = 'width: 100px; height: 40px;'
        self.fields['studentName'].widget.attrs['placeholder'] = 'Enter student name'
        self.fields['studentName'].widget.attrs['style'] = 'width: 400px; height: 40px;'
        self.fields['identification_number'].widget.attrs['placeholder'] = 'Student IC Number'
        self.fields['identification_number'].widget.attrs['style'] = 'width: 170px; height: 40px;'
        self.fields['birthdate'].widget.attrs['placeholder'] = 'Enter student birth date'
        self.fields['age'].widget.attrs['placeholder'] = 'Enter student age'
        self.fields['age'].widget.attrs['style'] = 'width: 50px; height: 40px;'

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 0:
            raise ValidationError("Age cannot be negative.")
        return age

    
    
class ModuleDetailsForm(forms.ModelForm):

    module_type = forms.CharField(max_length=20, required=True)
    module_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(max_length=255, required=True)
    book_instrument = forms.ModelChoiceField(queryset=ModuleDetails.objects.all())
    class Meta:
        model = ModuleDetails
        fields = ['module_type', 'module_name', 'description', 'bookInstrument']


class ActivityDetailsForm(forms.ModelForm):

    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select Student")
    class Meta:
        model = Activity
        fields = ['activity_name', 'activity_type', 'activity_date', 'start_time', 'end_time', 'location', 'description']
        labels = {
            'activity_name': 'Activity Name',
            'activity_type': 'Activity Type',
            'activity_date': 'Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'student': 'Student',
            'location': 'Location',
            'description': 'Description',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all()
        self.fields['student'].required = False

class ModuleForm(forms.ModelForm):
    class Meta:
        model = ModuleDetails
        fields = ['module_type', 'module_name', 'description', 'bookInstrument']

from django import forms
from .models import Book

class RegisterInstrumentForm(forms.Form):
    primary_instrument = forms.CharField(label='Primary Instrument', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Primary Instrument - e.g Guitar'}))
    variation = forms.CharField(label='Variation', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Variation - e.g. Electric'}))
    
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.none(),  # Start with an empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use a set to track unique book names
        unique_books = set()

        # Fetch all books from the database
        all_books = Book.objects.all()

        # Iterate over all books to collect unique book names
        for book in all_books:
            unique_books.add(book.book)  # Assuming 'name' is the attribute containing the book name

        # Create a queryset of Book objects filtered by unique book names
        unique_books_queryset = Book.objects.filter(book__in=unique_books)

        # Set the queryset for the books field
        self.fields['books'].queryset = unique_books_queryset

class BillingForm(forms.ModelForm):

    category = forms.ModelChoiceField(queryset=Instrument.objects.all(), empty_label='Select Instrument')

    class Meta:
        model = Billing
        fields = ['title', 'category', 'fee', 'description']
        labels = {
            'category': 'Instrument List'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Instrument.objects.all()
        self.fields['category'].widget.attrs['style'] = 'width: 400px; height: 40px;border-color:gray; border-radius:8px; padding:8px;'
        self.fields['category'].label_from_instance = lambda obj: f"{obj.instrument_minor_name} {obj.instrument_major_name}"    
   
