from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import parent_required
from administrator.models import Student, BookInstrument, ModuleDetails, Instrument, Teacher, auth_user_details, Activity, ParentLogin
from teacher.models import ProgressBar, Attendance
from django.template import loader
from django.contrib import messages
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
import json
from django.contrib.auth.decorators import login_required
from .forms import StudentPhotoForm
from xhtml2pdf import pisa 
from django.template.loader import get_template

@parent_required
def parent(request):
    if request.user.is_authenticated:
        # Get the authenticated user's details
        first_name = request.user.first_name
        last_name = request.user.last_name
        user_groups = request.user.groups.all()
        group_names = [group.name for group in user_groups]

        # Count the total students assigned to the parent
        total_students = Student.objects.filter(assigned_parent=request.user).count()
        
        # Count the total instruments (unique instruments) assigned to the parent's children
        total_instruments = Student.objects.filter(assigned_parent=request.user).values('instrument').distinct().count()

        # Get the list of students assigned to the parent
        students = Student.objects.filter(assigned_parent=request.user).annotate(
            pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
        )

        student_progress = []
        total_modules_all_children = 0  # Total modules taken by all children
        
        for student in students:
            # Calculate total modules for the specific book and instrument
            total_modules = ModuleDetails.objects.filter(
                bookInstrument__bookID_id=student.book_id,
                bookInstrument__instrumentID_id=student.instrument_id
            ).count()
            
            total_modules_all_children += total_modules  # Accumulate total modules

            # Calculate passed modules for the student
            pass_modules = ProgressBar.objects.filter(student=student, result__in=['3', '4', '5']).count()

            if total_modules > 0:
                progress_percentage = (pass_modules / total_modules) * 100
            else:
                progress_percentage = 0

            student_progress.append({
                'studentName': student.studentName,
                'progress_percentage': progress_percentage,
                'total_modules': total_modules  # Include total modules in student progress
            })

        # Retrieve login times for the current user
        login_times = ParentLogin.objects.filter(parent=request.user).values_list('login_time', flat=True)
        login_times = [login_time.isoformat() for login_time in login_times]

        # Pass the user data, group information, login times, total students, total instruments, and student progress to the template
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'groups': group_names,
            'total_students': total_students,
            'total_instruments': total_instruments,
            'login_times': json.dumps(login_times),  # Pass the login times to the template context
            'student_progress': json.dumps(student_progress),  # Pass student progress to the template context
            'total_modules_all_children': total_modules_all_children  # Pass total modules taken by all children
        }

        # Render the template with the context
        template = loader.get_template('master_parent.html')
        return HttpResponse(template.render(context, request))
    else:
        # Handle unauthenticated users as needed
        return HttpResponse("You are not logged in.")


@parent_required
def student_info(request):
    user = request.user
    students = None

    if user.groups.filter(name='parent').exists():
        students = Student.objects.filter(assigned_parent=user)
    elif user.groups.filter(name='teacher').exists():
        students = Student.objects.filter(assigned_teacher=user)

    if request.method == 'POST':
        form = StudentPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            student_id = request.POST.get('student_id')  # Retrieve student_id from POST data
            student = Student.objects.get(id=student_id)

            # Check if there is already a photo uploaded
            if student.picture:
                # If there is an existing photo, you can choose to delete it or overwrite it
                student.picture.delete()  # Delete the existing photo

            # Save the new photo
            student.picture = form.cleaned_data['picture']
            student.save()

            messages.success(request, 'Photo uploaded successfully')
            return redirect('student-information')  # Adjust this to your actual URL name
        else:
            messages.error(request, 'Error uploading photo')
    else:
        form = StudentPhotoForm()

    context = {
        'user': user,
        'students': students,
        'form': form,
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
    # Get the logged-in parent user object
    parent = request.user

    # Print debug information
    print(f"Logged-in parent: {parent}")

    # Get students related to this parent
    students = Student.objects.filter(assigned_parent=parent)

    # Print debug information
    print(f"Related students: {students}")

    # Retrieve all attendance records associated with the parent user
    all_attendance = Attendance.objects.filter(student__assigned_parent=parent)

    # Debug prints for verification
    print("All Attendance:", all_attendance)

    # Prepare a dictionary to store attendance details for each student
    attendance_data = {}
    total_attend_approved = 0
    total_attend_pending = 0
    total_absent_approved = 0
    total_absent_pending = 0

    # Fetch attendance data for each student
    for student in students:
        # Fetch attendance records for each student
        student_attendance = Attendance.objects.filter(student=student)

        # Calculate totals for this student
        for attendance in student_attendance:
            if attendance.attendance == 'Attend':
                if attendance.status == 'Approved':
                    total_attend_approved += 1
                elif attendance.status == 'Pending Verification':
                    total_attend_pending += 1
            elif attendance.attendance == 'Absent':
                if attendance.status == 'Approved':
                    total_absent_approved += 1
                elif attendance.status == 'Pending Verification':
                    total_absent_pending += 1

        # Store attendance data for this student
        attendance_data[student.id] = student_attendance

    # Print debug information
    print(f"Attendance data: {attendance_data}")

    # Render the template with context data
    return render(request, 'attendance.html', {
        'attendance_data': attendance_data,
        'attendance_list': all_attendance,  # Pass all_attendance to the template context
        'students': students,
        'total_attend_approved': total_attend_approved,
        'total_attend_pending': total_attend_pending,
        'total_absent_approved': total_absent_approved,
        'total_absent_pending': total_absent_pending,
    })

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

@parent_required
def media (request) :
    activities = Activity.objects.all()

    context = {
        'activities' : activities
    }
    
    return render(request, 'media_parent.html', context)

def activity_details(request, id):
    activity = get_object_or_404(Activity, id=id)
    albums = activity.album_set.all()  # Fetch all albums related to this activity
    
    return render(request, 'activity_details_parent.html', {'activity': activity, 'albums': albums})


def generate_report(request, student_id):
    # Fetch student based on student_id
    student = get_object_or_404(Student, id=student_id)

    # Fetch related data for the student
    book_instruments = BookInstrument.objects.filter(bookID=student.book, instrumentID=student.instrument)
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

    # Prepare data to be passed to the template
    context = {
        'student': student,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
        'module_types': set(module.module_type for module in module_details),
        'results_by_module': results_by_module,
    }

    # Render the template with context data
    template_path = 'report_template.html'
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="student_report_{student.id}.pdf"'

    # Generate PDF file
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response



def view_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Fetch related data for the student
    book_instruments = BookInstrument.objects.filter(bookID=student.book, instrumentID=student.instrument)
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)
    
    # Fetch progress bar objects for the student and modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)
    
    # Prepare results by module
    results_by_module = {}
    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module_id] = progress_bar.result
        print(f"Module ID: {progress_bar.module_id}, Result: {progress_bar.result}")
    
    
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
    
    # Prepare data to be passed to the template
    context = {
        'student': student,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
        'results_by_module': results_by_module,
        'module_details': module_details,
        'progress_bar' : progress_bar
    }
    
    return render(request, 'report_template.html', context)