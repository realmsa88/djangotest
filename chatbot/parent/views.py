from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import parent_required
from administrator.models import Student, BookInstrument, ModuleDetails, Instrument, Teacher, auth_user_details, Activity
from teacher.models import ProgressBar, Attendance
from django.template import loader
from django.contrib import messages
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

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
        student_book = student.book

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

@parent_required
def attendance(request):
    # Get the logged-in parent
    parent = request.user

    # Get the students related to this parent
    students = Student.objects.filter(assigned_parent=parent)

    # Prepare a dictionary to store attendance details for each student
   # Simplified view logic
    attendance_data = {}
    for student in students:
        attendance_data[student.id] = Attendance.objects.filter(student=student)

    context = {
        'students': students,
        'attendance_data': attendance_data,
    }

    return render(request, 'attendance.html', context)

def verify_attendance(request, student_id, attendance_id):
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        data = {
            'student_name': attendance.student.studentName,
            'attendance_title': attendance.title,
            'attendance_date': attendance.date,
            'attendance_start_time': attendance.start_time,
            'attendance_end_time': attendance.end_time,
        }
        return JsonResponse(data)
    except Attendance.DoesNotExist:
        return JsonResponse({'error': 'Attendance record not found'}, status=404)
    
@require_POST
def submit_absence(request):
    if request.method == 'POST':
        print(request.POST)  # Print POST data for debugging
        student_id = request.POST.get('student_id')
        attendance_id = request.POST.get('attendance_id')
        absence_reason = request.POST.get('absence_reason')

        if not student_id or not attendance_id:
            return HttpResponse("Error: Missing student_id or attendance_id.")

        try:
            attendance = Attendance.objects.get(id=attendance_id, student_id=student_id)
            attendance.absence_reason = absence_reason
            attendance.attendance = 'Absent' 
            attendance.save()
            messages.success(request, "Absence reason submitted successfully!")
            return redirect(reverse('attendance'))
        except Attendance.DoesNotExist:
            return HttpResponse("Attendance record not found.")
        except ValueError:
            return HttpResponse("Invalid attendance_id format.")

    return HttpResponse("Only POST requests are allowed.")



@parent_required
def leave(request):
    user = request.user
    students = Student.objects.filter(assigned_parent=user)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        title = request.POST.get('primary_instrument')
        attendance = request.POST.get('attendance')
        date = request.POST.get('activity_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')

        student = Student.objects.get(id=student_id)
        auth_user = auth_user_details.objects.get(user=student.assigned_teacher)
        teachers = Teacher.objects.filter(teacher=auth_user)

        if teachers.exists():
            teacher = teachers.first()  # Get the first teacher associated with the student

            Attendance.objects.create(
                student=student,
                teacher=teacher,
                title=title,
                attendance='Absent',
                description=description,
                date=date,
                start_time=start_time,
                end_time=end_time,
                status='Pending Verification'
            )

            messages.success(request, 'Leave request submitted successfully.')
        else:
            messages.error(request, 'No teacher found for the selected student.')

        return redirect('leave')

    return render(request, 'leave.html', {'students': students})

@parent_required
def activity_list(request) :

    category = request.GET.get('category')
    if category:
        activities = Activity.objects.filter(activity_type=category)
    else:
        activities = Activity.objects.all()

    activity_types = Activity.objects.values_list('activity_type', flat=True).distinct()
   
    return render(request,'activities_list.html',{
        'activities': activities,
        'activity_types': activity_types,
    })