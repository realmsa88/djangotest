from django.shortcuts import render
from .decorators import teacher_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from administrator.models import Student, Teacher, Instrument, Book, BookInstrument, ModuleDetails, auth_user_details
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from collections import defaultdict, Counter
from .models import ProgressBar, Attendance
from django.contrib import messages
from django.db.models import Count, F, Q
from django.views.decorators.http import require_POST
import json, logging
from pytz import timezone as pytz_timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# Create your views here.

@teacher_required
def teacher(request):
    # Ensure that the user is authenticated
    if request.user.is_authenticated:
        # Access the first name and last name of the authenticated user
        first_name = request.user.first_name
        last_name = request.user.last_name
        
        # You can also access other user attributes if needed
        # username = request.user.username
        # email = request.user.email
        
        # Pass the user data to the template
        context = {
            'first_name': first_name,
            'last_name': last_name
        }
        
        # Load the template and render it with the context
        template = loader.get_template('master_teacher.html')
        return HttpResponse(template.render(context, request))
    else:
        # Redirect or handle unauthenticated users as needed
        # For example, you might want to redirect them to the login page
        return HttpResponse("")
    

@teacher_required
def teaching_modules(request):
    # Get the logged-in user
    user = request.user

    # Get all teacher objects associated with the logged-in user
    teachers = Teacher.objects.filter(teacher__user=user)

    # Collect all instruments associated with these teachers
    instruments = Instrument.objects.filter(id__in=teachers.values_list('instrument_id', flat=True))

    # Get all unique major names
    instrument_majors = instruments.values_list('instrument_major_name', flat=True).distinct()

    # Get all book IDs associated with these instruments
    book_ids = BookInstrument.objects.filter(instrumentID__in=instruments).values_list('bookID', flat=True)

    # Get all books corresponding to the retrieved book IDs
    books = Book.objects.filter(id__in=book_ids)

    # Pass the instruments, books, and instrument majors to the template
    context = {
        'instruments': instruments,
        'books': books,
        'instrument_majors': instrument_majors,
    }

    return render(request, 'teaching_modules.html', context)


@teacher_required
def student_progress(request, instrument_minor, instrument_major, book_id):
    teacher = request.user

    # Fetch students assigned to the teacher with the specified instrument and book
    students = Student.objects.filter(
        assigned_teacher=teacher,
        instrument__instrument_major_name=instrument_major,
        instrument__instrument_minor_name=instrument_minor,
        book_id=book_id
    ).annotate(
        pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
    )

    for student in students:
        # Calculate total modules for the specific book and instrument
        total_modules = ModuleDetails.objects.filter(bookInstrument__bookID_id=book_id,
                                                     bookInstrument__instrumentID_id=student.instrument_id).count()
        # Calculate passed modules for the student
        pass_modules = ProgressBar.objects.filter(student=student, result__in=['3', '4', '5']).count()

        if total_modules > 0:
            student.progress_percentage = (pass_modules / total_modules) * 100
        else:
            student.progress_percentage = 0

        student.remaining_progress_percentage = 100 - student.progress_percentage

        # Additional debugging output
        print(f"Student: {student.studentName}, Total Modules: {total_modules}, Passed Modules: {pass_modules}")
        print(f"Progress Percentage: {student.progress_percentage}")
        print(f"Remaining Progress Percentage: {student.remaining_progress_percentage}")

    context = {
        'students': students,
        'instrument_major': instrument_major,
        'instrument_minor': instrument_minor,
        'book_id': book_id,
    }

    return render(request, 'student_progress.html', context)

@teacher_required
def student_results(request, student_name):
    student = get_object_or_404(Student, studentName=student_name)
    student_instrument = student.instrument
    student_book = student.book

    # Get the related BookInstrument entries for the student's book and instrument
    book_instruments = BookInstrument.objects.filter(bookID=student_book, instrumentID=student_instrument)

    if not book_instruments.exists():
        return HttpResponse("No matching BookInstrument found for the student's book.")
    
    # Get ModuleDetails entries that relate to the BookInstrument entries
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)

    module_types = set(module.module_type for module in module_details)
    results_by_module = {module: [] for module in module_details}

    # Get ProgressBar entries for the student and the modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module].append(progress_bar.result)
    
    # Calculate progress for Practice modules
    practice_modules = module_details.filter(module_type='Practice')
    total_practice_modules = practice_modules.count()
    passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3','4', '5']).count()
    practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0

    # Calculate progress for Repertoire modules
    repertoire_modules = module_details.filter(module_type='Repertoire')
    total_repertoire_modules = repertoire_modules.count()
    passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3','4', '5']).count()
    repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0

    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        result = request.POST.get('result')
        
        module = get_object_or_404(ModuleDetails, id=module_id)
        progress_bar, created = ProgressBar.objects.get_or_create(student=student, module=module)
        progress_bar.result = result
        progress_bar.save()
        
        messages.success(request, f'Result for {module.module_name} updated successfully.')
        return redirect('student_results', student_name=student_name)

    context = {
        'student': student,
        'book_id': student_book.id,
        'instrument_major_name': student_instrument.instrument_major_name,
        'instrument_minor_name': student_instrument.instrument_minor_name,
        'module_types': module_types,
        'results_by_module': results_by_module,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
    }

    return render(request, 'student_results.html', context)





@teacher_required
def update_student_result(request, student_name):
    student = get_object_or_404(Student, studentName=student_name)
    student_instrument = student.instrument
    student_book = student.book

    # Get the related BookInstrument entries for the student's book and instrument
    book_instruments = BookInstrument.objects.filter(bookID=student_book, instrumentID=student_instrument)

    if not book_instruments.exists():
        return HttpResponse("No matching BookInstrument found for the student's book.")
    
    # Get ModuleDetails entries that relate to the BookInstrument entries
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)

    module_types = set(module.module_type for module in module_details)
    results_by_module = {module: [] for module in module_details}

    # Get ProgressBar entries for the student and the modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module].append(progress_bar.result)
    
    # Calculate progress for Practice modules
    practice_modules = module_details.filter(module_type='Practice')
    total_practice_modules = practice_modules.count()
    passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3','4', '5']).count()
    practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0

    # Calculate progress for Repertoire modules
    repertoire_modules = module_details.filter(module_type='Repertoire')
    total_repertoire_modules = repertoire_modules.count()
    passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3','4', '5']).count()
    repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0

    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        result = request.POST.get('result')
        
        module = get_object_or_404(ModuleDetails, id=module_id)
        progress_bar, created = ProgressBar.objects.get_or_create(student=student, module=module)
        progress_bar.result = result
        progress_bar.save()
        
        messages.success(request, f'Result for {module.module_name} updated successfully.')
        return redirect('student_results', student_name=student_name)

    context = {
        'student': student,
        'book_id': student_book.id,
        'instrument_major_name': student_instrument.instrument_major_name,
        'instrument_minor_name': student_instrument.instrument_minor_name,
        'module_types': module_types,
        'results_by_module': results_by_module,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
    }

    return render(request, 'student_results.html', context)


def pass_values(request):
    # Retrieve 'PASS' values from your data source
    pass_values = [...]  # Retrieve pass values from your database or any other source
    return JsonResponse({'pass_values': pass_values})

def attendance(request):
    user = request.user

    # Get all teacher objects associated with the logged-in user
    teachers = Teacher.objects.filter(teacher__user=user)

    # Collect all instruments associated with these teachers
    instruments = Instrument.objects.filter(id__in=teachers.values_list('instrument_id', flat=True))

    # Get all unique major names
    instrument_majors = instruments.values_list('instrument_major_name', flat=True).distinct()

    # Get all book IDs associated with these instruments
    book_ids = BookInstrument.objects.filter(instrumentID__in=instruments).values_list('bookID', flat=True)

    # Get all books corresponding to the retrieved book IDs
    books = Book.objects.filter(id__in=book_ids)

    # Pass the instruments, books, and instrument majors to the template
    context = {
        'instruments': instruments,
        'books': books,
        'instrument_majors': instrument_majors,
    }
    # Render the 'student_attendance.html' template
    return render(request, 'student_attendance.html', context)



from .models import Teacher
from django.template.loader import render_to_string
from django.http import JsonResponse

def get_attendance(request, student_id):
    # Retrieve attendance details for the given student
    attendance_details = Attendance.objects.filter(student_id=student_id).values('date', 'status', 'title', 'description', 'end_time', 'start_time')

    # Return the attendance details as JSON response
    return JsonResponse({'attendance_details': list(attendance_details)})



@login_required
def student_list_by_book(request, instrument_minor, instrument_major, book_id):
    user = request.user
    try:
        # Assuming auth_user_details is the related model to User that Teacher uses
        auth_user = auth_user_details.objects.get(user=user)
        teachers = Teacher.objects.filter(teacher=auth_user)  # Get the Teacher instances using auth_user_details
    except auth_user_details.DoesNotExist:
        return redirect('student-attendance')

    if not teachers.exists():
        return redirect('student-attendance')

    # Get the book
    book = get_object_or_404(Book, pk=book_id)

    # Filter students by the user (not the Teacher instance)
    students = Student.objects.filter(
        assigned_teacher=user,
        instrument__instrument_major_name=instrument_major,
        instrument__instrument_minor_name=instrument_minor,
        book_id=book_id
    ).annotate(
        pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
    )

    # Fetch attendance records for each student
    for student in students:
        student.attendance = Attendance.objects.filter(student=student).values('title', 'date','description', 'status', 'end_time', 'start_time', 'attendance')

    context = {
        'book': book,
        'students': students,
        'instrument_minor': instrument_minor,
        'instrument_major': instrument_major
    }
    return render(request, 'students_by_book.html', context)


logger = logging.getLogger(__name__)

@csrf_exempt
def attend_student(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            # Get current local time
            current_time = datetime.now().time()
            print(f"Current time: {current_time}")
            print(f"User: {user.username}")

            ongoing_class = Attendance.objects.filter(
                teacher_email=user,
                start_time__lte=current_time,
                end_time__gte=current_time
            ).first()

            if ongoing_class:
                # Get the attendance ID of the ongoing class
                attendance_id = ongoing_class.id

                # Update the status of the ongoing class
                ongoing_class.status = 'Approved'
                ongoing_class.save()

                return JsonResponse({
                    'success': True,
                    'status': 'Approved',
                    'student_name': ongoing_class.student.studentName,
                    'start_time': ongoing_class.start_time.strftime("%I:%M %p"),
                    'end_time': ongoing_class.end_time.strftime("%I:%M %p"),
                    'attendance_id': attendance_id
                })
            else:
                print("No ongoing class found")
                return JsonResponse({'success': False, 'error': 'No ongoing class found at the current time for the current teacher.'})
        else:
            print("User not authenticated")
            return JsonResponse({'success': False, 'error': 'User not authenticated.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    
def students_for_date(request, date):
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    current_time = datetime.now().time()
    students = Attendance.objects.filter(date=selected_date).select_related('student')
    
    student_data = []
    for attendance in students:
        start_time = attendance.start_time
        end_time = attendance.end_time
        is_ongoing = start_time <= current_time <= end_time
        
        student_data.append({
            'name': attendance.student.studentName,
            'start_time': start_time.strftime("%H:%M:%S"),
            'end_time': end_time.strftime("%H:%M:%S"),
            'is_ongoing': is_ongoing
        })

    return JsonResponse({'students': student_data})





from datetime import datetime, time


def student_attendance_view(request):
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    ongoing_classes = Attendance.objects.filter(date=current_date, start_time__lte=current_time, end_time__gte=current_time)
    context = {
        'ongoing_classes': ongoing_classes,
        'current_date': current_date,
    }
    return render(request, 'student_attendance.html', context)



@login_required
def attendance_list(request):
    # Get the current user details
    current_user = request.user

    # Retrieve the corresponding auth_user_details instance
    try:
        user_details = auth_user_details.objects.get(user=current_user)
    except auth_user_details.DoesNotExist:
        # Handle the case where no auth_user_details instance is found
        user_details = None

    # Retrieve all attendance records associated with the current user
    if user_details:
        all_attendance = Attendance.objects.filter(teacher_email=user_details.user)
    else:
        all_attendance = []

    # Debug prints for verification
    print("Current User:", current_user)
    print("All Attendance:", all_attendance)

    return render(request, 'attendance_list.html', {'attendance_list': all_attendance})



@require_POST
def verify_attendance(request):
    # Get attendance_id from POST data
    attendance_id = request.POST.get('attendance_id')

    # Ensure attendance_id is valid and not empty
    if attendance_id:
        try:
            # Attempt to retrieve Attendance object by id
            attendance = Attendance.objects.get(id=int(attendance_id))
            attendance.status = 'Approved'
            attendance.save()
            return redirect('attendance-list')
        except (ValueError, ObjectDoesNotExist) as e:
            # Handle errors when retrieving or updating attendance
            print(f"Error verifying attendance: {e}")
            # Redirect back to attendance-list with error message in query parameters
            return redirect('attendance-list', error='Attendance record not found or could not be verified.')
    else:
        # Handle case where attendance_id is empty
        print("Attendance ID is empty.")
        # Redirect back to attendance-list with error message in query parameters
        return redirect('attendance-list', error='Attendance ID is empty or invalid.')



def activity_list_teacher(request):
    return render(request,'activity_list_teacher.html')