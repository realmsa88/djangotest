from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import parent_required
from administrator.models import Student, BookInstrument, ModuleDetails, Instrument
from teacher.models import ProgressBar
from django.template import loader

# Create your views here.
# @csrf_exempt
@parent_required
def parent(request):
    # Ensure that the user is authenticated
    if request.user.is_authenticated:
        # Access the first name and last name of the authenticated user
        first_name = request.user.first_name
        last_name = request.user.last_name

         # Access the groups that the user belongs to
        user_groups = request.user.groups.all()
        
        # Extract group names from the user_groups queryset
        group_names = [group.name for group in user_groups]
        
        # Pass the user data and group information to the template
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'groups': group_names  # Pass the group names to the template context
        }
        
        # You can also access other user attributes if needed
        # username = request.user.username
        # email = request.user.email
        
        # Pass the user data to the template
       
        
        # Load the template and render it with the context
        template = loader.get_template('master_parent.html')
        return HttpResponse(template.render(context, request))
    else:
        # Redirect or handle unauthenticated users as needed
        # For example, you might want to redirect them to the login page
        return HttpResponse("You are not logged in.")


@parent_required
def student_info(request):
    user = request.user
    students = None

    # Assuming the logged-in user is a parent
    if user.groups.filter(name='parent').exists():
        # Retrieve the students associated with the parent
        students = Student.objects.filter(assigned_parent=user)
    # Assuming the logged-in user is a teacher
    elif user.groups.filter(name='teacher').exists():
        # Retrieve the students associated with the teacher
        students = Student.objects.filter(assigned_teacher=user)

    context = {
        'user': user,
        'students': students
    }

    return render(request, 'student_info.html', context)

@parent_required
def student_modules(request):
    user = request.user
    students = None
    students_data = []

    # Retrieve students associated with the user
    if user.groups.filter(name='parent').exists():
        students = Student.objects.filter(assigned_parent=user)
    elif user.groups.filter(name='teacher').exists():
        students = Student.objects.filter(assigned_teacher=user)

    for student in students:
        student_instrument = student.instrument
        student_book = student.current_book

        # Get the related BookInstrument entries for the student's book and instrument
        book_instruments = BookInstrument.objects.filter(bookID=student_book, instrumentID=student_instrument)

        # Get ModuleDetails entries that relate to the BookInstrument entries
        module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)

        results_by_module = {module: [] for module in module_details}

        # Get ProgressBar entries for the student and the modules found
        progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

        for progress_bar in progress_bar_objects:
            results_by_module[progress_bar.module].append(progress_bar.result)

        # Calculate progress for Practice modules
        practice_modules = module_details.filter(module_type='Practice')
        total_practice_modules = practice_modules.count()
        passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3', '4', '5']).count()
        practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0

        # Calculate progress for Repertoire modules
        repertoire_modules = module_details.filter(module_type='Repertoire')
        total_repertoire_modules = repertoire_modules.count()
        passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3', '4', '5']).count()
        repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0

        students_data.append({
            'student': student,
            'practice_completion_percentage': practice_completion_percentage,
            'repertoire_completion_percentage': repertoire_completion_percentage,
            'module_types': set(module.module_type for module in module_details),
            'results_by_module': results_by_module
        })

    context = {
        'user': user,
        'students_data': students_data,
        'students': students
    }

    return render(request, 'student_learning.html', context)


def attendance(request):
    return render(request,'attendance.html')
